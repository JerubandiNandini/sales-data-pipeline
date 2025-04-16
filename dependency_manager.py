import subprocess
import sys
import os
import logging
import venv

class DependencyManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.venv_path = config.get('dependencies', {}).get('venv_path', '.venv')

    def ensure_venv(self):
        try:
            if not os.path.exists(self.venv_path):
                self.logger.info("Creating virtual environment")
                venv.create(self.venv_path, with_pip=True)
            pip_path = os.path.join(self.venv_path, 'bin' if os.name != 'nt' else 'Scripts', 'pip')
            return pip_path
        except Exception as e:
            self.logger.error(f"Failed to create virtual environment: {str(e)}")
            raise

    def install_dependencies(self):
        try:
            pip_path = self.ensure_venv()
            self.logger.info("Installing dependencies")
            subprocess.check_call([pip_path, 'install', '-r', 'requirements.txt'])
            self.logger.info("Dependencies installed successfully")
        except Exception as e:
            self.logger.error(f"Failed to install dependencies: {str(e)}")
            raise

def ensure_dependencies():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    dm = DependencyManager(config)
    dm.install_dependencies()