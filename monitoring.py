import psutil
import time
from prometheus_client import Counter, Gauge, start_http_server
import logging
from slack_sdk import WebClient
import os

rows_processed = Counter('sales_pipeline_rows_processed', 'Number of rows processed')
files_processed = Counter('sales_pipeline_files_processed', 'Number of files processed')
memory_usage = Gauge('sales_pipeline_memory_usage', 'Memory usage in MB')
execution_time = Gauge('sales_pipeline_execution_time', 'Execution time in seconds')
cpu_usage = Gauge('sales_pipeline_cpu_usage', 'CPU usage percentage')

class Monitor:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.slack_client = WebClient(token=os.getenv('SLACK_TOKEN', config.get('slack', {}).get('token', '')))
        start_http_server(8000)

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        cpu = psutil.cpu_percent()
        memory_usage.set(memory)
        execution_time.set(duration)
        cpu_usage.set(cpu)
        self.logger.info(f"Execution took {duration:.2f}s, used {memory:.2f}MB, CPU {cpu}%")
        if exc_val:
            self.send_slack_alert(f"Pipeline failed: {str(exc_val)}")

    def send_slack_alert(self, message):
        try:
            self.slack_client.chat_postMessage(
                channel=self.config['slack']['channel'],
                text=message
            )
            self.logger.info("Sent Slack alert")
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {str(e)}")

def monitor_health(config):
    return Monitor(config)

def expose_metrics(metrics):
    rows_processed.inc(metrics.get('rows_processed', 0))
    files_processed.inc(metrics.get('files_processed', 0))