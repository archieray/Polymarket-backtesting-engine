from polymarketdata import PolymarketDataClient
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
api_key = os.getenv("POLYMARKETDATA_API_KEY")

import requests

headers = {"x-api-key": api_key}

response = requests.get(
    "https://api.polymarketdata.co/v1/markets",
    headers=headers,
    params={
        "end_date_max": "2025-06-24T00:00:00Z",
        "tags": "2026-fifa-world-cup",
        "limit": 1000
    }
)
# print(response.status_code)
# print(response.json())
# data = response.json()
# closed_markets = [m for m in data['data'] if m['status'] == 'open']
# print(len(closed_markets))
