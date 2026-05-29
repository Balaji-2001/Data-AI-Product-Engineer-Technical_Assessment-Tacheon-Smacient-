# Task 2: Marketing Weather Pipeline

A small but complete data pipeline that fetches hourly weather data for key marketing cities, enriches it with a campaign viability score, and loads it to BigQuery — on a schedule, with error handling, and with a clear path to production.

---

## What API I Chose and Why

I used **[Open-Meteo](https://open-meteo.com/)** — a free, open-source weather API that requires no API key and returns clean structured JSON.

Three reasons I picked it over the other suggestions:

**1. Zero friction to run.** No API key means anyone cloning this repo can run it immediately without signing up for anything. That matters in an assessment context, and it also matters in a real team where you don't want pipeline setup blocked on credential provisioning.

**2. The data is marketing-relevant.** Weather has a genuine relationship with marketing performance — outdoor activations, event marketing, retail footfall, even digital ad spend patterns shift with weather. Building a pipeline that a martech team might actually use felt more interesting than pulling cryptocurrency prices.

**3. The data is non-trivial to work with.** The API returns nested hourly arrays, WMO weather codes that need decoding, and variables that need combining to be useful. It's a realistic data engineering problem, not a toy one.

---

## Project Structure

```
task-2/
├── pipeline/
│   ├── config.py       # All parameters — nothing is hardcoded in logic
│   ├── fetch.py        # API fetching with retries and error handling
│   ├── transform.py    # Cleaning, flattening, and derived fields
│   ├── load.py         # BigQuery load with explicit schema
│   └── main.py         # Entry point — orchestrates the full pipeline
├── queries/
│   └── summary.sql     # Three SQL queries against the loaded data
├── requirements.txt
├── .env.example
└── README.md           ← you are here
```

---

## How to Run the Pipeline

### Prerequisites

- Python 3.11+
- A Google account (for BigQuery Sandbox — free, no credit card)
- `gcloud` CLI installed

### Step 1: Clone and install

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo/task-2

pip install -r requirements.txt
```

### Step 2: Set up BigQuery

Go to [console.cloud.google.com/bigquery](https://console.cloud.google.com/bigquery). A default project is created automatically when you log in with a Google account. Copy your project ID.

### Step 3: Authenticate

```bash
gcloud auth application-default login
```

This sets up credentials that the Python BigQuery client picks up automatically — no need to manage key files.

### Step 4: Configure

```bash
cp .env.example .env
# Edit .env and set GCP_PROJECT_ID to your actual project ID
```

### Step 5: Run

```bash
cd pipeline
python main.py
```

To test without loading to BigQuery:

```bash
python main.py --dry-run
```

Expected output:
```
2026-05-29 07:14:22 | INFO     | __main__ | ============================================================
2026-05-29 07:14:22 | INFO     | __main__ | Pipeline run started | run_id=20260529_071422
2026-05-29 07:14:22 | INFO     | __main__ | STEP 1: Fetching data from Open-Meteo API
2026-05-29 07:14:23 | INFO     | fetch    | Fetching data for London (attempt 1/3)
2026-05-29 07:14:23 | INFO     | fetch    | Successfully fetched 48 hourly records for London
...
2026-05-29 07:14:26 | INFO     | __main__ | STEP 2: Transforming and enriching data
2026-05-29 07:14:26 | INFO     | transform| Transform complete for London: 48 rows, 24 columns
...
2026-05-29 07:14:26 | INFO     | __main__ | STEP 3: Loading to BigQuery
2026-05-29 07:14:28 | INFO     | load     | Load job complete. Rows added this run: 240. Total rows in table: 240.
2026-05-29 07:14:28 | INFO     | __main__ | Pipeline run SUCCEEDED | run_id=20260529_071422 | elapsed=6.2s
```

---

## BigQuery Setup and Schema

The pipeline creates the dataset and table automatically on first run. No manual setup in the BigQuery console required.

**Dataset:** `marketing_weather`  
**Table:** `hourly_conditions`

Key columns:

| Column | Type | Description |
|---|---|---|
| `city` | STRING | City name |
| `timestamp` | STRING | ISO 8601 local timestamp |
| `date` | DATE | Calendar date |
| `temperature_c` | FLOAT64 | Air temperature (°C) |
| `precipitation_mm` | FLOAT64 | Precipitation (mm) |
| `windspeed_kmh` | FLOAT64 | Wind speed (km/h) |
| `weathercode` | INTEGER | WMO weather code |
| `weather_description` | STRING | Human-readable weather label |
| `campaign_viability_score` | FLOAT64 | **Derived: 0–10 outdoor marketing suitability score** |
| `campaign_viability_label` | STRING | **Derived: Excellent / Good / Fair / Poor / Unsuitable** |
| `time_of_day` | STRING | Morning / Afternoon / Evening / Night |
| `day_type` | STRING | Weekday or Weekend |
| `season` | STRING | Spring / Summer / Autumn / Winter |
| `ingested_at` | STRING | UTC timestamp of when the row was ingested |

---

## The Derived Field: Campaign Viability Score

This is the most important thing I added. The raw API gives you temperature, wind, precipitation, and UV index. That's useful but requires a human to interpret. The `campaign_viability_score` combines them into a single 0–10 number that answers: **"is this a good time for an outdoor marketing event?"**

Scoring logic:
- Starts at 10 (perfect conditions)
- Deducted for temperature outside 15–28°C comfort range
- Deducted heavily for precipitation above 1mm
- Deducted for wind above 30 km/h
- Deducted for high UV (above index 6)
- Floored to 0 for thunderstorm weather codes

The thresholds are in `config.py` and can be tuned per-market. A team running campaigns in Mumbai will have different comfort thresholds than one in London.

---

## SQL Summary Query and Output

Three queries are in `queries/summary.sql`. Here's Query 1 (daily summary) with sample output:

```sql
SELECT
    city, date, avg_temp_c,
    total_precipitation_mm,
    avg_viability_score,
    good_hours_count,
    dominant_viability_label
FROM daily_summary
WHERE date = CURRENT_DATE() - 1
ORDER BY avg_viability_score DESC;
```

**Sample output:**

| city | date | avg_temp_c | total_precipitation_mm | avg_viability_score | good_hours_count | dominant_viability_label |
|---|---|---|---|---|---|---|
| Mumbai | 2026-05-28 | 31.4 | 0.0 | 7.2 | 18 | Good |
| Delhi | 2026-05-28 | 33.1 | 0.0 | 6.8 | 15 | Good |
| New York | 2026-05-28 | 22.3 | 0.2 | 8.1 | 20 | Excellent |
| Manchester | 2026-05-28 | 14.6 | 3.4 | 4.3 | 6 | Fair |
| London | 2026-05-28 | 15.2 | 2.1 | 5.1 | 9 | Fair |

Query 3 (city rankings) output:

| city | avg_score | excellent_hours | good_hours | pct_usable_hours |
|---|---|---|---|---|
| New York | 8.1 | 14 | 9 | 95.8 |
| Mumbai | 7.2 | 8 | 12 | 83.3 |
| Delhi | 6.8 | 5 | 11 | 66.7 |
| London | 5.1 | 2 | 8 | 41.7 |
| Manchester | 4.3 | 1 | 5 | 25.0 |

---

## BigQuery Sandbox Limitations (and How I Worked Around Them)

The Sandbox doesn't support:
- **DML operations** (INSERT, UPDATE, DELETE, MERGE) — I use `WRITE_APPEND` load jobs instead, which are supported
- **Table expiry** is set automatically (60 days) — acceptable for a pipeline assessment; would use a paid account for production
- **Streaming inserts** — not needed; batch loads work fine for daily runs

The pipeline is designed entirely around batch loads, which work perfectly in the Sandbox. No DML queries needed anywhere.

---

## Production Thinking (Step 5)

### How would you schedule this pipeline to run automatically?

**Short answer: Google Cloud Scheduler + Cloud Run Jobs.**

The pipeline is already a single `python main.py` call. Containerise it with a Dockerfile, deploy it as a Cloud Run Job, and trigger it with a Cloud Scheduler cron (`0 7 * * *` for 7am daily). Total setup: about 2 hours.

The reason I'd use Cloud Run over Cloud Functions or a VM: it's ephemeral (no idle costs), it scales to zero, and it handles the container lifecycle without manual management. For a pipeline that runs once a day, you pay for about 10–15 seconds of compute.

Alternative: if the team already uses Apache Airflow or Prefect, wrap the pipeline steps into a DAG. The fetch → transform → load structure maps cleanly to tasks.

### How would you know if it failed?

Three layers:

1. **Exit codes.** The pipeline exits 0 on success, 1 on partial failure, 2 on full failure. Cloud Scheduler treats non-zero exits as failures and can alert on them.

2. **Cloud Logging.** Every log line goes to Cloud Logging automatically when running in Cloud Run. Set up a log-based alert on `ERROR` level messages from the pipeline, triggered to a Slack channel or email.

3. **Data freshness check.** A simple monitoring query runs on a schedule (e.g. every morning at 8am, one hour after the pipeline):

```sql
SELECT
    MAX(DATE(ingested_at)) AS last_ingest_date,
    DATE_DIFF(CURRENT_DATE(), MAX(DATE(ingested_at)), DAY) AS days_since_last_ingest
FROM `project.marketing_weather.hourly_conditions`;
```

If `days_since_last_ingest > 1`, fire an alert. This catches cases where the pipeline "succeeded" (exit 0) but produced no rows — which pure exit-code monitoring would miss.

### What would you add or change if this pipeline needed to scale to 10x the data volume?

Currently: 5 cities × 48 hours × ~20 columns = ~240 rows per run. At 10x that's still tiny — BigQuery handles this trivially.

The real scaling question is: what if we go from 5 cities to 500? Or from 1 API to 10 APIs?

**At 50 cities:** The fetches are currently sequential. Add `concurrent.futures.ThreadPoolExecutor` to parallelise API calls. Open-Meteo allows concurrent requests; 50 parallel fetches would finish in the same time as 5.

**At 500 cities:** Move to an async fetch pattern (httpx with asyncio). Also consider batching the BigQuery loads rather than one load per run.

**At 10 APIs:** The single-file pipeline becomes a maintenance problem. Move to a plugin architecture where each connector is an independent class implementing a common interface (`fetch()`, `transform()`, `schema()`). Main orchestrates by loading the connectors dynamically.

**For all of the above:** Add proper idempotency. Right now, running the pipeline twice in one day creates duplicate rows. Fix this by adding a `run_date` partition and checking for existing records before loading, or by using BigQuery MERGE instead of APPEND (requires a paid account).

---

## What I'd Do Differently With More Time

**Testing.** There are no unit tests here, and that's the thing I'm least comfortable with. The transform logic — especially the `campaign_viability_score` function — should have a proper test suite with edge cases (nulls, extreme values, thunderstorm codes). Ten minutes of writing tests would have caught two bugs I found manually during development.

**Idempotency.** Running the pipeline twice creates duplicate rows. The fix is straightforward — check for existing rows with the same `city` + `date` + `hour` before loading — but it requires a BigQuery MERGE which isn't available in the Sandbox. I'd address this on a paid account.

**The derived field is opinionated.** The campaign viability score uses thresholds I defined. A real team would want to validate those thresholds against historical data — does a score of 7 actually correlate with better outdoor campaign performance? I've built the structure; the calibration needs real data.

**Connector pattern.** Right now, adding a new API means editing `fetch.py` and `transform.py`. With more time I'd introduce a simple `Connector` base class so new data sources are genuinely plug-in.
