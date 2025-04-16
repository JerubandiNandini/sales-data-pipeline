import pandas as pd
import plotly.express as px
import os
import logging

class DataVisualizer:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.output_dir = config['visualization']['output_dir']
        os.makedirs(self.output_dir, exist_ok=True)

    def visualize(self, data, forecasts):
        try:
            self.plot_sales_over_time(data, forecasts)
            self.plot_top_products(data)
            self.logger.info("Generated visualizations")
        except Exception as e:
            self.logger.error(f"Visualization failed: {str(e)}")
            raise

    def plot_sales_over_time(self, data, forecasts):
        sales_by_date = data.groupby(data['date'].dt.to_period('M'))['sales'].sum().reset_index()
        sales_by_date['date'] = sales_by_date['date'].astype(str)
        fig = px.line(sales_by_date, x='date', y='sales', title='Sales Over Time')
        if not forecasts.empty:
            forecasts['ds'] = forecasts['ds'].dt.to_period('M').astype(str)
            fig.add_scatter(x=forecasts['ds'], y=forecasts['yhat'], mode='lines', name='Forecast')
        output_path = os.path.join(self.output_dir, 'sales_over_time.html')
        fig.write_html(output_path)
        fig.write_image(os.path.join(self.output_dir, 'sales_over_time.png'))
        self.logger.info(f"Saved sales over time plot")

    def plot_top_products(self, data):
        top_products = data.groupby('product')['sales'].sum().nlargest(5).reset_index()
        fig = px.pie(top_products, names='product', values='sales', title='Top 5 Products')
        output_path = os.path.join(self.output_dir, 'top_products.html')
        fig.write_html(output_path)
        fig.write_image(os.path.join(self.output_dir, 'top_products.png'))
        self.logger.info(f"Saved top products plot")