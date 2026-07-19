import pandas as pd
import requests

TOKEN_ID = "18984892750376483805253418990318943016541056782864991219807572406261231770929"
OUTPUT_FILE = "data/earthquakes_14_16.csv"


def fetch_and_save(token_id, output_file):
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
