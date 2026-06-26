from polymarketdata import PolymarketDataClient
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
api_key = os.getenv("POLYMARKETDATA_API_KEY")

import requests

headers = {"x-api-key": api_key}

bins = {
    "finish_last": [],
    "win_group": [],
    "head_to_head": [],
    "elimination_stage": [],
}

STOP_VERBS = {"finish", "win", "advance", "reach", "qualify", "make", "be", "top"}

## Function idea: basically run manual_test on a large scale, grouping markets into 4 categories
## Categories can be found in question_types, filtering based on keywords
## Setting fidelity to 30 minutes, because speed isn't really the main thing for my purposes
## Yes and No have different tokens, so always picks the YES token just for consistency.

def extract_team_name(question):
    words = question.removeprefix("Will ").split()
    team_words = []
    for word in words:
        if word.lower().rstrip("?.,") in STOP_VERBS:
            break
        team_words.append(word)
    return "_".join(w.lower() for w in team_words)


def fetch_world_cup_markets():
    markets = []
    cursor = None

    while True:
        params = {"tags": "2026-fifa-world-cup", "limit": 1000, "min_liquidity": 10000}
        if cursor:
            params["cursor"] = cursor

        response = requests.get(
            "https://api.polymarketdata.co/v1/markets",
            headers=headers,
            params=params
        )

        payload = response.json()
        markets.extend(payload["data"])

        cursor = payload["metadata"].get("next_cursor")
        if not cursor or len(payload["data"]) < 1000:
            break

    for market in markets:
        name = market.get("question")
        tokens = market.get("tokens")
        token_id = tokens[1]['id'] if tokens else None

        name_lower = name.lower()
        team = extract_team_name(name)

        if "finish last" in name_lower:
            filename = f"{team}_finish_last"
            bins["finish_last"].append({"name": name, "token_id": token_id, "filename": filename})
            fetch_and_save(token_id, filename)
        elif "win group" in name_lower:
            filename = f"{team}_win_group"
            bins["win_group"].append({"name": name, "token_id": token_id, "filename": filename})
            fetch_and_save(token_id, filename)
        elif any(kw in name_lower for kw in ["advance to the round", "reach the quarter", "reach the semi", "reach the final", "win the 2026 fifa world cup"]):
            filename = f"{team}_elimination_stage"
            bins["elimination_stage"].append({"name": name, "token_id": token_id, "filename": filename})
            fetch_and_save(token_id, filename)

    for bin_name, entries in bins.items():
        print(f"=== {bin_name} ({len(entries)} markets) ===")
        for e in entries:
            print(f"  {e['name']} | {e['filename']}.csv")
        print()

    return bins


def fetch_and_save(token_id, filename):
    response = requests.get(
        "https://clob.polymarket.com/prices-history",
        params={
            "market": token_id,
            "interval": "max",
            "fidelity": 30
        }
    )

    df = pd.DataFrame(response.json()['history'])
    df = df.rename(columns={"t": "time", "p": "prices"})
    df['market_id'] = token_id
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.to_csv(f'data/{filename}.csv')
    print(df.head())


if __name__ == "__main__":
    fetch_world_cup_markets()
