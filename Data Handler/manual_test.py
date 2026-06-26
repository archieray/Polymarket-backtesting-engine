## This was just to help me build the bigger function, I left it in because i feel like i'll come back to it
## The event chosen for this was "WILL NORWAY TOP THEIR GROUP"

from polymarketdata import PolymarketDataClient
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
api_key = os.getenv("POLYMARKETDATA_API_KEY")

import requests

headers = {"x-api-key": api_key}

response1 = requests.get(
    "https://api.polymarketdata.co/v1/markets",
    headers=headers,
    params={
        "tags": "2026-fifa-world-cup",
        "limit": 1000
    }
)

print(response1.json())


# token_id = '36982737812609801400501176287982677104372661602083682910520606276456764515825'

# response = requests.get(
#     "https://clob.polymarket.com/prices-history",
#     params={
#         "market": token_id,
#         "interval": "max",
#         "fidelity": 1
#     }
# )

# df = pd.DataFrame(response.json()['history'])
# df = df.rename(columns={"t":"time", "p":"prices"})
# df['market_id'] = token_id
# df['time'] = pd.to_datetime(df['time'],unit = 's')
# df.to_csv('data/norway_test_try.csv')
# print(df.head())

