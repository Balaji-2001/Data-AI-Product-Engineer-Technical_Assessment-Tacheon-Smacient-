"""
fetch.py
--------
Handles all communication with the Open-Meteo API.

Responsibilities:
- Build the request for each location
- Retry on transient failures
- Return raw JSON or raise a structured error
- Never crash silently — every failure is logged with enough context to debug
"""

import logging
import time
from typing import Optional

import requests
from requests.exceptions import ConnectionError, ReadTimeout, HTTPError

from config import (
    API_BASE_URL,
    HOURLY_VARIABLES,
    LOCATIONS,
    MAX_RETRIES,
    PAST_DAYS,
    REQUEST_TIMEOUT_SECONDS,
    RETRY_BACKOFF_SECONDS,
)

logger = logging.getLogger(__name__)


class APIFetchError(Exception):
    """Raised when a location fetch fails after all retries."""
    pass


def _build_params(location: dict) -> dict:
    """
    Build the query parameter dict for a single location.
    Keeping this separate makes it easy to test and to change
    without touching the request logic.
    """
    return {
        "latitude":    location["latitude"],
        "longitude":   location["longitude"],
        "hourly":      ",".join(HOURLY_VARIABLES),
        "timezone":    location["timezone"],
        "past_days":   PAST_DAYS,
        "forecast_days": 1,
    }


def fetch_location(location: dict) -> Optional[dict]:
    """
    Fetch weather data for a single location from the Open-Meteo API.

    Retries up to MAX_RETRIES times on connection errors or server errors.
    Returns raw API JSON on success, or raises APIFetchError after all retries fail.

    Args:
        location: A dict with keys: name, latitude, longitude, timezone

    Returns:
        dict: Raw JSON response from Open-Meteo

    Raises:
        APIFetchError: If the request fails after all retries
    """
    params = _build_params(location)
    city = location["name"]

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Fetching data for {city} (attempt {attempt}/{MAX_RETRIES})")

            response = requests.get(
                API_BASE_URL,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

            # Raise immediately on 4xx/5xx — no point retrying a 400
            response.raise_for_status()

            data = response.json()

            # Basic sanity check: API should return hourly data
            if "hourly" not in data:
                raise ValueError(f"Unexpected response shape for {city}: 'hourly' key missing")

            logger.info(
                f"Successfully fetched {len(data['hourly']['time'])} hourly records for {city}"
            )
            return data

        except (ConnectionError, ReadTimeout) as e:
            # Network-level failures — worth retrying
            logger.warning(f"Network error for {city} on attempt {attempt}: {e}")
            if attempt < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_BACKOFF_SECONDS}s...")
                time.sleep(RETRY_BACKOFF_SECONDS)

        except HTTPError as e:
            status = e.response.status_code if e.response else "unknown"
            logger.error(f"HTTP {status} error for {city}: {e}")
            # Don't retry client errors (4xx) — they won't fix themselves
            if e.response and 400 <= e.response.status_code < 500:
                raise APIFetchError(f"Client error for {city}: HTTP {status}") from e
            # Retry server errors (5xx)
            if attempt < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_BACKOFF_SECONDS}s...")
                time.sleep(RETRY_BACKOFF_SECONDS)

        except ValueError as e:
            # Unexpected response shape — not a network issue, don't retry
            logger.error(f"Data validation error for {city}: {e}")
            raise APIFetchError(str(e)) from e

        except Exception as e:
            # Catch-all so one location failure doesn't kill the whole run
            logger.error(f"Unexpected error fetching {city}: {type(e).__name__}: {e}")
            raise APIFetchError(f"Unexpected error for {city}") from e

    raise APIFetchError(
        f"Failed to fetch data for {city} after {MAX_RETRIES} attempts"
    )


def fetch_all_locations() -> list[dict]:
    """
    Fetch data for all configured locations.

    Failures for individual locations are logged and skipped —
    one bad location does not block the rest.

    Returns:
        list of (location_config, raw_api_response) tuples for successful fetches
    """
    results = []
    failed = []

    for location in LOCATIONS:
        try:
            raw = fetch_location(location)
            results.append({"location": location, "data": raw})
        except APIFetchError as e:
            logger.error(f"Skipping {location['name']}: {e}")
            failed.append(location["name"])

    if failed:
        logger.warning(f"Pipeline completed with {len(failed)} failed location(s): {failed}")
    else:
        logger.info(f"All {len(results)} locations fetched successfully")

    return results
