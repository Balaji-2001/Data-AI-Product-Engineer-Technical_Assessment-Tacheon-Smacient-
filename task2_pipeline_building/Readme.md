# Task 2: Pipeline Building

## What this pipeline does
This pipeline pulls hourly weather data from the Open-Meteo public API, transforms the JSON into a tabular pandas DataFrame, adds derived fields, and loads the result into BigQuery.

## Why Open-Meteo
Open-Meteo is a free public API with structured JSON output and no API key required for basic use. That makes it a simple and reliable choice for this assessment.

## Files
- `main.py`: fetches, transforms, and loads the data
- `config.py`: central configuration values
- `.env.example`: environment variable template
- `requirements.txt`: Python dependencies
- `sql/summary_query.sql`: example SQL summary
- `data/transformed_sample.csv`: sample transformed output
- `logs/pipeline.log`: run logs

## Setup
1. Create a BigQuery Sandbox project.
2. Create a dataset and table in BigQuery.
3. Copy `.env.example` to `.env`.
4. Fill in your project, dataset, and table values.

## Install dependencies
```bash
pip install -r requirements.txt
```

## Run the pipeline
```bash
python main.py
```

## BigQuery connection
The script uses the BigQuery Python client and loads a pandas DataFrame into a BigQuery table using `load_table_from_dataframe()`.

## SQL summary
The SQL file groups rows by city and temperature band, then shows counts and average/max values.

## Production thinking
### Scheduling
This pipeline could run on a cron schedule, GitHub Actions, Airflow, or Cloud Scheduler.

### Failure detection
Use logging, retries, and job status checks. Failures should be visible in logs and alerts.

### Scaling to 10x data
If data volume grows, use partitioned tables, batch loading, schema control, and separate raw/transformed layers.