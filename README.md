## Clone
```bash
git clone https://github.com/JerubandiNandini/sales-data-pipeline.git


##keep the files in below folder structure to run
##Verify all 27 files are in the correct folders:
.github/workflows/ has ci-cd.yaml
docs/ has generate_docs.py
great_expectations/expectations/ has sales_data.json
k8s/ has deployment.yaml
tests/ has test_automation.py, test_data_cleaner.py
Root has main.py, README.md, etc.



# Ultra-Advanced Automated Sales Data Pipeline

This project automates sales data processing with cutting-edge Python automation.

## Features
- AI-powered cleaning with autoencoders.
- Real-time streaming with Kafka and dynamic scaling.
- Interactive Streamlit dashboard.
- Predictive analytics with Prophet.
- NLP-generated multi-language reports.
- Kubernetes deployment and CI/CD.
- Data quality monitoring with Great Expectations.
- Advanced automation: scheduling, Slack alerts, email delivery, backups, webhooks, dependency management, and documentation.

## Setup
1. Install dependencies:
   ```bash
   python dependency_manager.py
   ```
2. Start Kafka (for streaming):
   ```bash
   docker-compose up -d
   ```
3. Configure `config.yaml` (Slack token, email credentials, etc.).
4. Place input CSVs in `./data`.

## Running
Batch mode:
```bash
python main.py --mode batch --input sample_sales_data.csv --output cleaned_sales_data.csv
```
Streaming mode:
```bash
python main.py --mode stream
```
Scheduled mode:
```bash
python main.py --mode schedule
```
Dashboard:
```bash
streamlit run dashboard.py
```
Webhook trigger:
```bash
curl -X POST http://localhost:8001/trigger_pipeline -d '{"mode": "batch"}'
```

## Docker
```bash
docker build -t sales-pipeline .
docker run -v $(pwd)/:/app -p 8501:8501 -p 8001:8001 sales-pipeline
```

## Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
```

## Testing
```bash
python -m unittest discover tests
```

## Monitoring
- Prometheus metrics: `http://localhost:8000`
- Logs: `sales_pipeline.log`
- Slack alerts: Configured channel
- Email reports: Sent to configured recipients

## Output
- Cleaned data: `cleaned_*.csv`
- Visualizations: `visualizations/`
- Reports: `reports/`
- State: `pipeline_state.json`
- Backups: `backups/`
- Docs: `docs/`

## Configuration
Edit `config.yaml` for schedules, Kafka, Slack, email, backups, scaling, and webhooks.