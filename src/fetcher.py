import requests
from py_clob_client.client import ClobClient
import pandas as pd
from datetime import datetime

GAMMA_BASE = "https://gamma-api.polymarket.com"
CLOB_BASE = "https://clob.polymarket.com"
DATA_BASE = "https://data-api.polymarket.com"

def get_active_markets(limit=50, tag=None):
    url = f"{GAMMA_BASE}/markets"
    params = {"limit": limit, "active": "true"}
    if tag:
        params["tag"] = tag
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    # Adjust based on actual response shape (usually data['data'] or list)
    markets = data.get('data', data) if isinstance(data, dict) else data
    return pd.DataFrame(markets)

def get_market_price(token_id: str):
    client = ClobClient(CLOB_BASE)  # read-only
    price = client.get_price(token_id=token_id)
    return price

def get_trades(market_id: str, limit=100):
    url = f"{DATA_BASE}/trades"
    params = {"market": market_id, "limit": limit}
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()

# Example usage
if __name__ == "__main__":
    df = get_active_markets(limit=10)
    print(df[["question", "volume"]].head())  # adjust column names after first run
