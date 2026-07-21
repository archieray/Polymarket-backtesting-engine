import requests

# From Polymarket's published fee schedule - feeRate per market category.
FEE_RATES_BY_CATEGORY = {
    "Crypto": 0.07,
    "Sports": 0.05,
    "Finance": 0.04,
    "Politics": 0.04,
    "Economics": 0.05,
    "Culture": 0.05,
    "Weather": 0.05,
    "Other / General": 0.05,
    "Mentions": 0.04,
    "Tech": 0.04,
    "Geopolitics": 0.0,
}
DEFAULT_FEE_RATE = FEE_RATES_BY_CATEGORY["Other / General"]


def resolve_fee_rate(token_id):
    # token_id -> parent market -> parent event -> tags -> match a tag label
    # against a known fee category. Falls back to the default (with a loud
    # warning, not a silent guess) if no tag matches - getting this wrong
    # directly skews backtest correctness, so it shouldn't fail quietly.
    market_resp = requests.get(
        "https://gamma-api.polymarket.com/markets",
        params={"clob_token_ids": token_id},
    )
    markets = market_resp.json()
    if not markets:
        raise ValueError(f"no market found for token id {token_id}")

    event_slug = markets[0]["events"][0]["slug"]

    event_resp = requests.get(
        "https://gamma-api.polymarket.com/events",
        params={"slug": event_slug},
    )
    events = event_resp.json()
    tags = events[0].get("tags", []) if events else []

    for tag in tags:
        label = tag.get("label")
        if label in FEE_RATES_BY_CATEGORY:
            return FEE_RATES_BY_CATEGORY[label]

    labels = [t.get("label") for t in tags]
    print(
        f"WARNING: no matching fee category for token {token_id} "
        f"(tags: {labels}) - falling back to default rate {DEFAULT_FEE_RATE}"
    )
    return DEFAULT_FEE_RATE
