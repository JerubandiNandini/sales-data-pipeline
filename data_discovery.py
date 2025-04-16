import os
import glob
import logging

class DataDiscovery:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.input_dir = config.get('data_discovery', {}).get('input_dir', '.')

    def discover_files(self):
        try:
            files = glob.glob(os.path.join(self.input_dir, '*.csv'))
            self.logger.info(f"Discovered {len(files)} CSV files in {self.input_dir}")
            return files
        except Exception as e:
            self.logger.error(f"Data discovery failed: {str(e)}")
            return []