# One-off fetch for a single market's YES token price history, saved as a
# CSV for data_handler/data_handler.py to read. Not general/parameterized yet -
# this pulls exactly one market ("How many 7.0+ earthquakes in 2026?", the
# 14-16 outcome bin) since that's the only one being backtested so far.

import pandas as pd
import requests

# The 14-16 bin's YES token id, found via Polymarket's public Gamma API
# (https://gamma-api.polymarket.com/events?slug=...) - no API key needed,
# unlike the paid polymarketdata.co service used by the old World Cup scripts.
TOKEN_ID = "18984892750376483805253418990318943016541056782864991219807572406261231770929"
OUTPUT_FILE = "data/earthquakes_14_16.csv"


def fetch_and_save(token_id, output_file):
    # Polymarket's public CLOB endpoint - interval="max" pulls the full
    # available history at 30-min fidelity (fidelity will need to be much
    # finer for anything closer to live trading; fine for a first backtest).
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
    df.to_csv(output_file)

    print(f"{len(df)} rows written to {output_file}")
    print(df.head())


if __name__ == "__main__":
    fetch_and_save(TOKEN_ID, OUTPUT_FILE)
