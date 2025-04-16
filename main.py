import prefect
from prefect import flow, task
import pandas as pd
import yaml
import logging
import schedule
import time
import os
from data_cleaner import DataCleaner
from data_analyzer import DataAnalyzer
from data_visualizer import DataVisualizer
from report_generator import ReportGenerator
from kafka_consumer import KafkaConsumer
from great_expectations.dataset import PandasDataset
import great_expectations as ge
from monitoring import monitor_health, expose_metrics
from config_watcher import ConfigWatcher
from data_discovery import DataDiscovery
from state_manager import StateManager
from backup_manager import BackupManager
from dependency_manager import ensure_dependencies
from docs.generate_docs import generate_docs
from multiprocessing import Pool

def setup_logging():
    import structlog
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    logging.config.fileConfig('logging_config.yaml', disable_existing_loggers=False)

@task
def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

@task
def validate_data(data, logger):
    ge_df = ge.from_pandas(data)
    ge_df.expect_column_values_to_not_be_null("sales")
    ge_df.expect_column_values_to_be_of_type("date", "datetime64")
    results = ge_df.validate()
    if not results["success"]:
        logger.error("Data quality validation failed")
        raise ValueError("Data quality check failed")
    logger.info("Data quality validation passed")

def process_file(args):
    file, config, output_file = args
    logger = logging.getLogger(__name__)
    state_manager = StateManager(config)
    if not state_manager.is_processed(file):
        data = pd.read_csv(file)
        validate_data(data, logger)
        logger.info(f"Loaded batch data from {file} with {len(data)} rows")
        cleaner = DataCleaner(config)
        cleaned_data = cleaner.clean(data)
        analyzer = DataAnalyzer(config)
        stats, forecasts = analyzer.analyze(cleaned_data)
        cleaned_data.to_csv(output_file, index=False)
        visualizer = DataVisualizer(config)
        visualizer.visualize(cleaned_data, forecasts)
        report_gen = ReportGenerator(config)
        report_gen.generate_report(cleaned_data, stats, forecasts)
        state_manager.mark_processed(file)
        expose_metrics({"rows_processed": len(cleaned_data), "files_processed": 1})
        return len(cleaned_data)
    return 0

@flow
def sales_pipeline(mode="batch", input_file="sample_sales_data.csv", output_file="cleaned_sales_data.csv"):
    ensure_dependencies()
    setup_logging()
    logger = prefect.context.get_run_context().logger
    config = load_config()
    state_manager = StateManager(config)
    backup_manager = BackupManager(config)

    try:
        with monitor_health(config):
            if mode == "batch":
                backup_manager.backup_input(input_file)
                data_discovery = DataDiscovery(config)
                files = data_discovery.discover_files()
                pool_size = min(len(files), config['scaling']['max_processes'])
                if pool_size > 1:
                    with Pool(pool_size) as pool:
                        results = pool.map(process_file, [(f, config, f"cleaned_{os.path.basename(f)}") for f in files])
                    total_rows = sum(results)
                    logger.info(f"Processed {len(files)} files with {total_rows} rows")
                else:
                    for file in files:
                        process_file((file, config, output_file))
                generate_docs()

            elif mode == "stream":
                kafka_consumer = KafkaConsumer(config)
                kafka_consumer.consume()
                logger.info("Started Kafka streaming consumer")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        state_manager.rollback()
        backup_manager.restore()
        raise

def run_scheduled():
    config = load_config()
    schedule.every().day.at(config["schedule"]["batch_time"]).do(sales_pipeline, mode="batch")
    config_watcher = ConfigWatcher(config, load_config)
    config_watcher.start()
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Automated Sales Data Pipeline")
    parser.add_argument('--mode', choices=['batch', 'stream', 'schedule'], default='batch', help='Processing mode')
    args = parser.parse_args()
    
    if args.mode == "schedule":
        run_scheduled()
    else:
        sales_pipeline(mode=args.mode)