#!/usr/bin/env python
"""
Fetch concurrent-player count from Valve's official API.
Usage:
    python src/collectors/steam_api.py 620980          # Beat Saber
"""
import sys, time, json, datetime as dt, pathlib, os, requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("STEAM_API_KEY")
if not KEY:
    raise SystemExit("STEAM_API_KEY missing in .env")

APP_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 620980
RAW = pathlib.Path("data/raw"); RAW.mkdir(parents=True, exist_ok=True)

url = (
    "https://api.steampowered.com/ISteamUserStats/"
    "GetNumberOfCurrentPlayers/v1/"
)
resp = requests.get(url, params={"appid": APP_ID, "key": KEY}, timeout=15)
resp.raise_for_status()

payload = resp.json()        # {"response":{"player_count":1234,"result":1}}
payload["fetched_at"] = int(time.time())
stamp = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
out = RAW / f"steamapi_{APP_ID}_{stamp}.json"
json.dump(payload, out.open("w"))
print(f"✅  Saved Steam API snapshot → {out}")
