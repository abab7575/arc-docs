"""Call precheck before checkout and read proves, stale, and checked_ago honestly.

Set PRECHECK_USER_AGENT to the name of your agent. The fallback is a placeholder.
Set PRECHECK_URL to a mock in CI. This file does not fetch the store and it
does not call a model.
"""

from __future__ import annotations

import json
import math
import os
import time
import urllib.error
import urllib.parse
import urllib.request

# Set PRECHECK_USER_AGENT to the name of your agent. The fallback is a placeholder.
USER_AGENT = os.environ.get("PRECHECK_USER_AGENT", "my-agent/1.0 (+https://example.com/contact)")
DEFAULT_ENDPOINT = "https://www.arcreport.ai/api/precheck"
DAY_S = 24 * 60 * 60
_CACHE: dict[str, tuple[float, dict]] = {}
EXAMPLE_URL = "https://allbirds.com/products/shoe"

LIMITS = {
    "checked_ago": 'Coarse age of last_checked, copied unchanged. "never checked" means the check time is missing or unparseable. null means the saved time is in the future, so no age is stated.',
    "stale": "Copied unchanged. True when last_checked is 24 hours old or older, or the check time is missing or unparseable. False only when the saved check is newer than 24 hours.",
    "proves": "Copied unchanged from each rail. The sentence describes that saved status. It does not prove an agent completed checkout. null rails means ARC returned no proves sentence.",
    "reachable_checkout": "Copied unchanged. True only when a saved check returned a checkout link. False when that check finished without one. null when there is no completed check. This is not an agent that finished checkout.",
}


def endpoint() -> str:
    return os.environ.get("PRECHECK_URL", DEFAULT_ENDPOINT)


def _store_host(url: str) -> str:
    parsed = urllib.parse.urlparse(url if "://" in url else "https://" + url)
    host = (parsed.hostname or url).lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    return host


def _retry_after_seconds(header: str | None) -> int:
    if not header or not header.strip():
        return 60
    try:
        seconds = float(header)
    except ValueError:
        seconds = None
    if seconds is not None and math.isfinite(seconds) and seconds >= 0:
        return math.ceil(seconds)
    try:
        from email.utils import parsedate_to_datetime
        when = parsedate_to_datetime(header)
    except (TypeError, ValueError, IndexError, OverflowError):
        return 60
    if when is None:
        return 60
    return max(0, math.ceil(when.timestamp() - time.time()))


def fetch_precheck(url: str) -> dict:
    host = _store_host(url)
    saved = _CACHE.get(host)
    # One saved answer per host for 24 hours. The limit is 60 requests a minute.
    if saved and time.time() - saved[0] < DAY_S:
        return saved[1]
    target = endpoint() + "?" + urllib.parse.urlencode({"url": url})
    request = urllib.request.Request(
        target,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 429:
            # Respect Retry-After. Do not retry in a loop.
            wait = _retry_after_seconds(error.headers.get("Retry-After"))
            raise RuntimeError("rate limited, retry after " + str(wait) + " s") from None
        raise
    if not isinstance(payload, dict):
        raise RuntimeError("precheck response was not a JSON object")
    _CACHE[host] = (time.time(), payload)
    return payload


def honest(body: dict) -> dict:
    """Copy the saved fields. Do not rewrite a missing check into a fresh one."""
    rails = body.get("rails")
    copied = None
    if isinstance(rails, list):
        copied = [
            {"name": rail.get("name"), "status": rail.get("status"), "proves": rail.get("proves")}
            for rail in rails
            if isinstance(rail, dict)
        ]
    return {
        "host": body.get("host"),
        "known": body.get("known"),
        "reachable_checkout": body.get("reachable_checkout"),
        "checked_ago": body.get("checked_ago"),
        "stale": body.get("stale"),
        "rails": copied,
        "limits": LIMITS,
    }


def reading_for(url: str) -> dict:
    return honest(fetch_precheck(url))


def main() -> None:
    url = os.environ.get("PRECHECK_EXAMPLE_URL", EXAMPLE_URL)
    print(json.dumps({"reading": reading_for(url)}))


if __name__ == "__main__":
    main()
