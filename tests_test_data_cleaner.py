import unittest
import pandas as pd
from data_cleaner import DataCleaner

class TestDataCleaner(unittest.TestCase):
    def setUp(self):
        self.config = {
            'schema': {'expected_columns': ['date', 'product', 'sales']}
        }
        self.cleaner = DataCleaner(self.config)
        self.data = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', None],
            'product': ['Product A', None, 'Product B'],
            'sales': [100.0, None, 200.0]
        })

    def test_clean(self):
        cleaned_data = self.cleaner.clean(self.data.copy())
        self.assertFalse(cleaned_data['sales'].isnull().any())
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(cleaned_data['date']))

    def test_batch_cleaning(self):
        large_data = pd.concat([self.data] * 1000, ignore_index=True)
        cleaned_data = self.cleaner.clean(large_data)
        self.assertFalse(cleaned_data['sales'].isnull().any())
        self.assertEqual(len(cleaned_data), len(large_data))

if __name__ == '__main__':
    unittest.main()