#!/usr/bin/env python
"""
Collect live viewer totals for a single game.
Usage: python src/collectors/twitch.py 33214       # Beat Saber (Twitch game_id)
"""
import os, sys, pathlib, time, datetime as dt, requests, json
from dotenv import load_dotenv; load_dotenv()

ID  = os.getenv("TWITCH_CLIENT_ID")
SEC = os.getenv("TWITCH_CLIENT_SECRET")
if not ID or not SEC:
    raise SystemExit("⚠️  Twitch creds missing in .env")

GAME_ID = sys.argv[1] if len(sys.argv) > 1 else "33214"  # Beat Saber default
RAW = pathlib.Path("data/raw"); RAW.mkdir(parents=True, exist_ok=True)

# ----- get or refresh app token ------------------------------------------------
token_resp = requests.post(
    "https://id.twitch.tv/oauth2/token",
    params=dict(client_id=ID, client_secret=SEC, grant_type="client_credentials"),
    timeout=15,
)
token = token_resp.json()["access_token"]

headers = {"Client-ID": ID, "Authorization": f"Bearer {token}"}
url     = "https://api.twitch.tv/helix/streams"

resp = requests.get(url, headers=headers,
                    params={"game_id": GAME_ID, "first": 100}, timeout=15)
resp.raise_for_status()

payload = {
    "fetched_at": int(time.time()),
    "game_id": GAME_ID,
    "streams": resp.json()["data"],      # list of live channels
}

stamp = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
out   = RAW / f"twitch_{GAME_ID}_{stamp}.json"
json.dump(payload, out.open("w"))
print("✅  Saved Twitch snapshot →", out)
