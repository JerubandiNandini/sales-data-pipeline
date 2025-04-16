import os
import shutil
import logging
from datetime import datetime
import json
import glob

class BackupManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.backup_dir = config.get('backup', {}).get('backup_dir', 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)

    def backup_input(self, input_file):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(self.backup_dir, f"input_{timestamp}_{os.path.basename(input_file)}")
            shutil.copy(input_file, backup_path)
            self.logger.info(f"Backed up input file to {backup_path}")
        except Exception as e:
            self.logger.error(f"Failed to backup input: {str(e)}")

    def backup_state(self, state):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(self.backup_dir, f"state_{timestamp}.json")
            with open(backup_path, 'w') as f:
                json.dump(state, f)
            self.logger.info(f"Backed up state to {backup_path}")
        except Exception as e:
            self.logger.error(f"Failed to backup state: {str(e)}")

    def restore_state(self):
        try:
            backups = sorted(glob.glob(os.path.join(self.backup_dir, 'state_*.json')))
            if backups:
                with open(backups[-1], 'r') as f:
                    state = json.load(f)
                self.logger.info(f"Restored state from {backups[-1]}")
                return state
            self.logger.warning("No state backups found")
            return {"processed_files": [], "last_state": None}
        except Exception as e:
            self.logger.error(f"Failed to restore state: {str(e)}")
            return {"processed_files": [], "last_state": None}