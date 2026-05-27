import os
import logging
from datetime import datetime, timezone

import pandas as pd
import requests
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

API_URL = "https://api.open-meteo.com/v1/forecast"

CITIES = [
    {"city": "Chennai", "latitude": 13.0827, "longitude": 80.2707},
    {"city": "Bengaluru", "latitude": 12.9716, "longitude": 77.5946},
]

HOURLY_FIELDS = "temperature_2m,relative_humidity_2m,wind_speed_10m"

BQ_PROJECT_ID = os.getenv("BQ_PROJECT_ID")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID")
BQ_TABLE_ID = os.getenv("BQ_TABLE_ID")


def fetch_weather(city):
    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "hourly": HOURLY_FIELDS,
        "timezone": "Asia/Kolkata"
    }
    try:
        logging.info(f"Fetching data for {city['city']}")
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"API error for {city['city']}: {e}")
        return None


def transform_data(city, payload):
    if not payload or "hourly" not in payload:
        return pd.DataFrame()

    hourly = payload["hourly"]
    df = pd.DataFrame(hourly)

    df["city"] = city["city"]
    df["latitude"] = city["latitude"]
    df["longitude"] = city["longitude"]

    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df["temperature_2m"] = pd.to_numeric(df["temperature_2m"], errors="coerce")
    df["relative_humidity_2m"] = pd.to_numeric(df["relative_humidity_2m"], errors="coerce")
    df["wind_speed_10m"] = pd.to_numeric(df["wind_speed_10m"], errors="coerce")

    df = df.dropna(subset=["time", "temperature_2m"])

    df["temp_band"] = pd.cut(
        df["temperature_2m"],
        bins=[-100, 20, 30, 100],
        labels=["cool", "warm", "hot"]
    )

    df["is_hot_hour"] = df["temperature_2m"] > 30
    df["ingested_at"] = datetime.now(timezone.utc)

    return df


def load_to_bigquery(df):
    if df.empty:
        logging.warning("No data to load into BigQuery.")
        return

    client = bigquery.Client(project=BQ_PROJECT_ID)
    table_id = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_TABLE_ID}"

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND"
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    logging.info(f"Loaded {len(df)} rows to {table_id}")


def main():
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    frames = []

    for city in CITIES:
        payload = fetch_weather(city)
        df = transform_data(city, payload)
        if not df.empty:
            frames.append(df)

    if not frames:
        logging.warning("No data returned from API.")
        return

    final_df = pd.concat(frames, ignore_index=True)

    final_df.to_csv("data/transformed_sample.csv", index=False)

    load_to_bigquery(final_df)


if __name__ == "__main__":
    main()
