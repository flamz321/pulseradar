import requests
import pandas as pd
import json
from py_clob_client.client import ClobClient

# Polymarket
GAMMA_BASE = "https://gamma-api.polymarket.com"
DATA_BASE = "https://data-api.polymarket.com"
CLOB_BASE = "https://clob.polymarket.com"

# Kalshi (public, no key needed)
KALSHI_BASE = "https://trading-api.kalshi.com/trade-api/v2"

def get_polymarket_markets(limit: int = 50, min_volume: float = 10000) -> pd.DataFrame:
    url = f"{GAMMA_BASE}/markets"
    params = {"active": "true", "limit": limit}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data)
    
    if df.empty:
        return pd.DataFrame()
    
    df = df[(df['active'] == True)]
    def safe_json(x):
        if isinstance(x, str) and x.startswith('['):
            try: return json.loads(x)
            except: return []
        return x if isinstance(x, list) else []
    
    df['outcomePrices'] = df['outcomePrices'].apply(safe_json)
    df['yes_price'] = df['outcomePrices'].apply(lambda x: float(x[0]) if len(x) > 0 else 0.5)
    
    numeric_cols = ['volumeNum', 'liquidityNum', 'oneDayPriceChange']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df = df[df['volumeNum'] >= min_volume]
    df['source'] = 'Polymarket'
    df['question'] = df['question']
    return df[['question', 'yes_price', 'volumeNum', 'oneDayPriceChange', 'category', 'source']]

def get_kalshi_markets(limit: int = 50) -> pd.DataFrame:
    url = f"{KALSHI_BASE}/markets"
    params = {"status": "open", "limit": limit}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json().get('markets', [])
    df = pd.DataFrame(data)
    
    if df.empty:
        return pd.DataFrame()
    
    df['yes_price'] = df.get('last_price', 0.5)
    df['volumeNum'] = df.get('volume', 0)
    df['oneDayPriceChange'] = 0.0  # Kalshi doesn't expose 24h % directly in list
    df['source'] = 'Kalshi'
    df['question'] = df['title']
    df['category'] = df.get('event_ticker', 'Other')
    return df[['question', 'yes_price', 'volumeNum', 'oneDayPriceChange', 'category', 'source']]

def get_active_markets(limit: int = 50, min_volume: float = 10000) -> pd.DataFrame:
    """Unified markets from BOTH Polymarket and Kalshi"""
    pm = get_polymarket_markets(limit=limit, min_volume=min_volume)
    kal = get_kalshi_markets(limit=limit)
    combined = pd.concat([pm, kal], ignore_index=True)
    combined = combined.sort_values('volumeNum', ascending=False)
    return combined

# Keep your existing get_trades (Polymarket-only for now) and get_midpoint
