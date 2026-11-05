"""
Product catalogue providers.

Both providers return a pandas DataFrame using the same columns as
data/products.csv (price_inr, processor, ram_gb, ...), plus provenance:

    source_name, source_type, source_url, fetched_at,
    rating, review_count, review_source_url, review_status, missing_specs

source_type is "api", "catalogue" (CSV row with a source_url) or "synthetic".
Nothing is invented: absent ratings stay None, and synthetic rows get no
fetched_at because they were never fetched from anywhere.
"""
import logging
import os
from pathlib import Path

import pandas as pd
import requests

from tools.provenance import classify_reviews, is_http_url, now_iso

log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "products.csv"

PROVENANCE_COLUMNS = [
    "source_url", "fetched_at", "rating", "review_count", "review_source_url",
]
# Numeric specs the scoring code needs; 0 means "not provided by the source".
NUMERIC_SPECS = ["ram_gb", "battery_wh", "weight_kg"]
TEXT_SPECS = ["processor", "storage", "gpu", "display", "build", "tags"]


def _none(value):
    return None if pd.isna(value) else value


def _finish(df: pd.DataFrame, source_name: str, default_type: str) -> pd.DataFrame:
    """Add computed provenance/review columns to a catalogue frame."""
    for col in PROVENANCE_COLUMNS:
        if col not in df.columns:
            df[col] = None

    source_types, statuses, ratings, counts = [], [], [], []
    for row in df.to_dict("records"):
        url = _none(row["source_url"])
        stype = default_type
        if default_type == "synthetic" and is_http_url(url):
            stype = "catalogue"

        rating = _none(row["rating"])
        rating = float(rating) if rating is not None else None
        count = _none(row["review_count"])
        count = int(count) if count is not None else None

        source_types.append(stype)
        ratings.append(rating)
        counts.append(count)
        statuses.append(
            classify_reviews(rating, count, _none(row["review_source_url"]), stype)
        )

    df["source_name"] = source_name
    df["source_type"] = source_types
    # dtype=object keeps counts as ints (a plain list with None becomes float).
    df["rating"] = pd.Series(ratings, index=df.index, dtype=object)
    df["review_count"] = pd.Series(counts, index=df.index, dtype=object)
    df["review_status"] = statuses
    return df


def load_csv_catalogue(path: Path = DATA_FILE) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Product dataset not found: {path}")

    df = pd.read_csv(path)
    df = _finish(df, "local_csv", "synthetic")
    df["missing_specs"] = [[] for _ in range(len(df))]
    return df


def load_api_catalogue(requirements: dict):
    """
    Generic JSON catalogue adapter. Returns a DataFrame, or None if the API is
    not configured or the call fails (the caller then falls back to the CSV).

    Env vars:
      PRODUCT_API_URL, PRODUCT_API_KEY
      PRODUCT_API_KEY_HEADER (default X-API-Key), PRODUCT_API_NAME

    FIELD_MAP is a PLACEHOLDER: edit it to match the real provider's response.
    """
    url = os.getenv("PRODUCT_API_URL", "")
    key = os.getenv("PRODUCT_API_KEY", "")
    if not (url and key):
        return None

    name = os.getenv("PRODUCT_API_NAME", "rest_api")
    header = os.getenv("PRODUCT_API_KEY_HEADER", "X-API-Key")

    field_map = {
        "items": "items", "product_id": "id", "brand": "brand",
        "model": "title", "price": "price", "currency": "currency",
        "url": "url", "rating": "rating", "review_count": "ratings_count",
        "specs": "specs",
    }

    try:
        resp = requests.get(
            url,
            params={
                "q": requirements.get("category", ""),
                "max_price": requirements.get("budget_max"),
            },
            headers={header: key},
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json().get(field_map["items"], [])
    except Exception as exc:  # network, quota, bad JSON: fall back to CSV
        log.warning("Product API failed (%s); using local CSV.", exc)
        return None

    fetched = now_iso()
    rows = []
    for it in items:
        # price_inr is an INR column; skip anything we cannot label honestly.
        if str(it.get(field_map["currency"], "INR")).upper() != "INR":
            continue
        specs = it.get(field_map["specs"], {}) or {}
        row = {
            "product_id": str(it[field_map["product_id"]]),
            "brand": it.get(field_map["brand"], "Unknown"),
            "model": it[field_map["model"]],
            "category": str(requirements.get("category", "")).lower(),
            "price_inr": float(it[field_map["price"]]),
            "source_url": it.get(field_map["url"]),
            "fetched_at": fetched,
            "rating": it.get(field_map["rating"]),
            "review_count": it.get(field_map["review_count"]),
            # Reviews are only checkable if the item page itself is the source.
            "review_source_url": it.get(field_map["url"]),
        }
        missing = []
        for col in NUMERIC_SPECS:
            if specs.get(col) is None:
                missing.append(col)
            row[col] = specs.get(col) if specs.get(col) is not None else 0
        for col in TEXT_SPECS:
            if specs.get(col) in (None, ""):
                missing.append(col)
            row[col] = specs.get(col) or ""
        row["missing_specs"] = missing
        rows.append(row)

    if not rows:
        return None

    return _finish(pd.DataFrame(rows), name, "api")


def load_catalogue(requirements: dict) -> pd.DataFrame:
    """API first (if configured), otherwise the local CSV."""
    df = load_api_catalogue(requirements)
    if df is not None:
        return df
    return load_csv_catalogue()
