import streamlit as st
import pandas as pd
import plotly.express as px
from data_analyzer import DataAnalyzer
from data_cleaner import DataCleaner
import yaml

st.title("Sales Data Dashboard")

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()
uploaded_file = st.file_uploader("Upload Sales Data", type=['csv'])
if uploaded_file:
    data = pd.read_csv(uploaded_file)
    cleaner = DataCleaner(config)
    cleaned_data = cleaner.clean(data)
    analyzer = DataAnalyzer(config)
    stats, forecasts = analyzer.analyze(cleaned_data)

    st.subheader("Sales Over Time")
    sales_by_date = cleaned_data.groupby(cleaned_data['date'].dt.to_period('M'))['sales'].sum().reset_index()
    sales_by_date['date'] = sales_by_date['date'].astype(str)
    fig = px.line(sales_by_date, x='date', y='sales')
    if not forecasts.empty:
        forecasts['ds'] = forecasts['ds'].dt.to_period('M').astype(str)
        fig.add_scatter(x=forecasts['ds'], y=forecasts['yhat'], mode='lines', name='Forecast')
    st.plotly_chart(fig)

    st.subheader("Top Products")
    top_products = cleaned_data.groupby('product')['sales'].sum().nlargest(5).reset_index()
    fig = px.pie(top_products, names='product', values='sales')
    st.plotly_chart(fig)

    st.subheader("Statistics")
    st.write(stats)