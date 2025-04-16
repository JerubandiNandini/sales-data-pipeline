import unittest
import os
from state_manager import StateManager
from backup_manager import BackupManager

class TestAutomation(unittest.TestCase):
    def setUp(self):
        self.config = {
            'state': {'file': 'test_state.json'},
            'backup': {'backup_dir': 'test_backups'}
        }
        os.makedirs('test_backups', exist_ok=True)

    def test_state_manager(self):
        sm = StateManager(self.config)
        sm.mark_processed("test.csv")
        self.assertTrue(sm.is_processed("test.csv"))
        sm.rollback()
        self.assertFalse(sm.is_processed("test.csv"))

    def test_backup_manager(self):
        bm = BackupManager(self.config)
        bm.backup_input("sample_sales_data.csv")
        backups = os.listdir('test_backups')
        self.assertTrue(any('input_' in b for b in backups))

    def tearDown(self):
        import shutil
        if os.path.exists('test_state.json'):
            os.remove('test_state.json')
        if os.path.exists('test_backups'):
            shutil.rmtree('test_backups')

if __name__ == '__main__':
    unittest.main()