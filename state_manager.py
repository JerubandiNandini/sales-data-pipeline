import json
import os
import logging
from datetime import datetime
from backup_manager import BackupManager

class StateManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.state_file = config.get('state', {}).get('file', 'pipeline_state.json')
        self.backup_manager = BackupManager(config)
        self.state = self.load_state()

    def load_state(self):
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            return {"processed_files": [], "last_state": None}
        except Exception as e:
            self.logger.error(f"Failed to load state: {str(e)}")
            return self.backup_manager.restore_state()

    def save_state(self):
        try:
            self.backup_manager.backup_state(self.state)
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f)
            self.logger.info("Saved pipeline state")
        except Exception as e:
            self.logger.error(f"Failed to save state: {str(e)}")

    def is_processed(self, file_path):
        return file_path in self.state["processed_files"]

    def mark_processed(self, file_path):
        self.state["processed_files"].append(file_path)
        self.state["last_state"] = datetime.now().isoformat()
        self.save_state()

    def rollback(self):
        self.logger.warning("Rolling back to previous state")
        self.state = self.backup_manager.restore_state()
        self.save_state()