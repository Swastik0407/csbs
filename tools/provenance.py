"""Helpers for source provenance and review-status classification."""
from datetime import datetime, timezone
from urllib.parse import urlparse


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def is_http_url(value) -> bool:
    """True only for absolute http(s) URLs (blocks javascript:, data:, etc.)."""
    if not isinstance(value, str) or not value.strip():
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def classify_reviews(rating, count, review_url, source_type) -> str:
    """
    verified   - rating + review count + a checkable URL, from a non-synthetic source
    unverified - a rating exists but cannot be checked
    missing    - no rating data (never invented)
    """
    if rating is None:
        return "missing"
    if (
        source_type != "synthetic"
        and count
        and is_http_url(review_url)
    ):
        return "verified"
    return "unverified"
