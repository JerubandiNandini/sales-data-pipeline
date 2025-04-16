import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from transformers import AutoModelForCausalLM
import psutil

class Autoencoder(nn.Module):
    def __init__(self, input_dim):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, input_dim),
            nn.Sigmoid()
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

class DataCleaner:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.autoencoder = Autoencoder(3).to(self.device)

    def get_batch_size(self, data_size):
        available_memory = psutil.virtual_memory().available / 1024 / 1024  # MB
        target_memory = available_memory * 0.5  # Use 50% of available memory
        estimated_row_size = 0.001  # Approx MB per row
        return min(data_size, max(100, int(target_memory / estimated_row_size)))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def clean(self, data):
        try:
            # Validate schema
            expected_columns = self.config['schema']['expected_columns']
            if not all(col in data.columns for col in expected_columns):
                raise ValueError("Invalid schema")

            # Process in batches
            batch_size = self.get_batch_size(len(data))
            cleaned_data = []
            for start in range(0, len(data), batch_size):
                batch = data.iloc[start:start + batch_size].copy()
                batch = batch.drop_duplicates()
                batch = self.handle_missing_values(batch)
                batch['date'] = pd.to_datetime(batch['date'], errors='coerce')
                batch['sales'] = pd.to_numeric(batch['sales'], errors='coerce')
                batch = self.detect_anomalies(batch)
                cleaned_data.append(batch)
                self.logger.info(f"Cleaned batch {start//batch_size + 1}, {len(batch)} rows")
            
            return pd.concat(cleaned_data, ignore_index=True)

        except Exception as e:
            self.logger.error(f"Cleaning failed: {str(e)}")
            raise

    def handle_missing_values(self, data):
        try:
            for column in ['sales']:
                if data[column].isnull().any():
                    data[column].fillna(data[column].mean(), inplace=True)
                    self.logger.info(f"Imputed {column} with mean (GAN placeholder)")
        except Exception as e:
            self.logger.warning(f"GAN imputation failed: {str(e)}, falling back to median")
            for column in ['sales']:
                if data[column].isnull().any():
                    data[column].fillna(data[column].median(), inplace=True)
                    self.logger.info(f"Imputed {column} with median (fallback)")
        return data

    def detect_anomalies(self, data):
        try:
            numeric_cols = ['sales']
            X = self.scaler.fit_transform(data[numeric_cols].fillna(0))
            X_tensor = torch.FloatTensor(X).to(self.device)
            with torch.no_grad():
                reconstructed = self.autoencoder(X_tensor)
                mse = torch.mean((X_tensor - reconstructed) ** 2, dim=1)
                threshold = mse.mean() + 2 * mse.std()
                anomalies = mse > threshold
            data.loc[anomalies.cpu().numpy(), 'sales'] = data['sales'].median()
            self.logger.info("Corrected anomalies with autoencoder")
        except Exception as e:
            self.logger.warning(f"Anomaly detection failed: {str(e)}, skipping")
        return data