# src/collectors/steam_charts.py
"""
Collect minute-level concurrent-player data from SteamCharts.

Usage (default Beat Saber):
    python src/collectors/steam_charts.py

Or pass a different Steam app-ID:
    python src/collectors/steam_charts.py 846470      # Half-Life: Alyx
"""

import sys
import time
import json
import datetime as dt
import pathlib
import requests

# ------------------------------------------------------------------------------
# 1. Settings ------------------------------------------------------------------
# ------------------------------------------------------------------------------

APP_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 620980  # Beat Saber
RAW_DIR = pathlib.Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    # Cloudflare blocks “python-requests” – spoof a real browser UA
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0 Safari/537.36"
    )
}

URL = f"https://steamcharts.com/app/{APP_ID}?output=json"

# ------------------------------------------------------------------------------
# 2. Fetch ---------------------------------------------------------------------
# ------------------------------------------------------------------------------

resp = requests.get(URL, headers=HEADERS, timeout=20)

# Helpful diagnostics if something goes wrong
if resp.status_code != 200:
    raise RuntimeError(
        f"[SteamCharts] HTTP {resp.status_code}\nFirst 120 bytes:\n{resp.text[:120]}"
    )

try:
    payload = resp.json()
except ValueError:
    # Most likely Cloudflare served HTML instead of JSON
    raise RuntimeError(
        "[SteamCharts] Response is not valid JSON. "
        "You may be rate-limited or blocked by Cloudflare."
    )

# ------------------------------------------------------------------------------
# 3. Save raw snapshot ---------------------------------------------------------
# ------------------------------------------------------------------------------

payload["fetched_at"] = int(time.time())  # when we fetched, not when Steam sampled
stamp = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
outfile = RAW_DIR / f"steam_{APP_ID}_{stamp}.json"

with outfile.open("w") as fp:
    json.dump(payload, fp)

print(f"✅  Saved Steam snapshot → {outfile}")
