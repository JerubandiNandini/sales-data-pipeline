from kafka import KafkaConsumer as KafkaClient
import pandas as pd
import json
import logging
from data_cleaner import DataCleaner
from tenacity import retry, stop_after_attempt, wait_exponential

class KafkaConsumer:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cleaner = DataCleaner(config)
        self.max_consumers = config['scaling']['max_kafka_consumers']

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
    def connect(self):
        return KafkaClient(
            self.config['kafka']['topic'],
            bootstrap_servers=self.config['kafka']['bootstrap_servers'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            group_id='sales_pipeline',
            max_poll_records=100
        )

    def consume(self):
        try:
            from multiprocessing import Process
            processes = []
            for _ in range(min(self.max_consumers, 2)):  # Dynamic scaling
                p = Process(target=self._consume_single)
                p.start()
                processes.append(p)
            for p in processes:
                p.join()
        except Exception as e:
            self.logger.error(f"Kafka consumer failed: {str(e)}")
            raise

    def _consume_single(self):
        consumer = self.connect()
        for message in consumer:
            data = pd.DataFrame([message.value])
            cleaned_data = self.cleaner.clean(data)
            self.logger.info(f"Processed streaming data: {cleaned_data.to_dict()}")