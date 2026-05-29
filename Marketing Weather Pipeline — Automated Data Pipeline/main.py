"""
main.py
-------
Entry point for the marketing weather pipeline.

Run this script to execute one full pipeline cycle:
    1. Fetch weather data for all configured cities
    2. Transform and enrich the data
    3. Load into BigQuery

Usage:
    python main.py

    # With custom log level:
    LOG_LEVEL=DEBUG python main.py

    # Dry run (fetch + transform only, no BigQuery load):
    python main.py --dry-run

Exit codes:
    0 = pipeline completed successfully
    1 = pipeline completed with errors (partial failure)
    2 = pipeline failed entirely (nothing loaded)
"""

import argparse
import logging
import sys
import time
from datetime import datetime

from config import LOG_DATE_FORMAT, LOG_FORMAT, LOG_LEVEL
from fetch import fetch_all_locations
from load import load_to_bigquery
from transform import transform_all


def setup_logging() -> None:
    """Configure logging for the whole pipeline."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[
            # Console output — enough for running locally and reading in Cloud Scheduler logs
            logging.StreamHandler(sys.stdout),
        ],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Marketing Weather Pipeline — fetch, transform, load to BigQuery"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run fetch and transform but skip BigQuery load. Useful for testing.",
    )
    return parser.parse_args()


def run_pipeline(dry_run: bool = False) -> int:
    """
    Execute the full pipeline.

    Returns:
        int: Exit code (0 = success, 1 = partial, 2 = full failure)
    """
    start_time = time.time()
    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info(f"Pipeline run started | run_id={run_id}")
    if dry_run:
        logger.info("DRY RUN MODE — BigQuery load will be skipped")
    logger.info("=" * 60)

    # -----------------------------------------------------------------------
    # Step 1: Fetch
    # -----------------------------------------------------------------------
    logger.info("STEP 1: Fetching data from Open-Meteo API")

    fetched = fetch_all_locations()

    if not fetched:
        logger.error("No data fetched. All locations failed. Exiting with code 2.")
        return 2

    logger.info(f"Fetch complete: {len(fetched)} location(s) successful")

    # -----------------------------------------------------------------------
    # Step 2: Transform
    # -----------------------------------------------------------------------
    logger.info("STEP 2: Transforming and enriching data")

    df = transform_all(fetched)

    if df.empty:
        logger.error("Transformation produced no rows. Exiting with code 2.")
        return 2

    logger.info(f"Transform complete: {len(df)} rows ready for load")

    # Quick preview for the logs — useful when running manually
    logger.info(f"Sample of transformed data (first 2 rows):\n{df.head(2).to_string()}")

    # -----------------------------------------------------------------------
    # Step 3: Load
    # -----------------------------------------------------------------------
    if dry_run:
        logger.info("STEP 3: Skipped (dry run). Would have loaded to BigQuery.")
        load_ok = True
    else:
        logger.info("STEP 3: Loading to BigQuery")
        load_ok = load_to_bigquery(df)

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    elapsed = round(time.time() - start_time, 2)

    logger.info("=" * 60)
    if load_ok:
        logger.info(f"Pipeline run SUCCEEDED | run_id={run_id} | elapsed={elapsed}s")
        exit_code = 0
    else:
        logger.error(f"Pipeline run FAILED at load step | run_id={run_id} | elapsed={elapsed}s")
        exit_code = 2
    logger.info("=" * 60)

    return exit_code


if __name__ == "__main__":
    setup_logging()
    args = parse_args()
    sys.exit(run_pipeline(dry_run=args.dry_run))
