import pandas as pd
from prophet import Prophet
import logging

class DataAnalyzer:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def analyze(self, data):
        try:
            # Summary statistics
            stats = {
                'mean': data['sales'].mean(),
                'median': data['sales'].median(),
                'std': data['sales'].std()
            }

            # Forecasting
            forecasts = self.forecast_sales(data)

            return stats, forecasts

        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            raise

    def forecast_sales(self, data):
        if 'date' in data.columns and 'sales' in data.columns:
            df_prophet = data[['date', 'sales']].rename(columns={'date': 'ds', 'sales': 'y'})
            model = Prophet(yearly_seasonality=True)
            model.fit(df_prophet)
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            self.logger.info("Generated sales forecast")
            return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        return pd.DataFrame()