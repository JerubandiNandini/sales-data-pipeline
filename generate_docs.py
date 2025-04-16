import os
import pydoc
import logging

def generate_docs():
    logger = logging.getLogger(__name__)
    try:
        modules = [
            'main', 'data_cleaner', 'data_analyzer', 'data_visualizer',
            'report_generator', 'kafka_consumer', 'config_watcher',
            'data_discovery', 'monitoring', 'email_sender', 'state_manager',
            'dependency_manager', 'backup_manager', 'webhook_server'
        ]
        os.makedirs('docs', exist_ok=True)
        for module in modules:
            pydoc.writedoc(module)
            html_file = f"{module}.html"
            if os.path.exists(html_file):
                os.rename(html_file, os.path.join('docs', html_file))
        logger.info("Generated API documentation in docs/")
    except Exception as e:
        logger.error(f"Failed to generate docs: {str(e)}")