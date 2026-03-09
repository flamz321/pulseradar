import requests
import pandas as pd
import json
from py_clob_client.client import ClobClient

GAMMA_BASE = "https://gamma-api.polymarket.com"
DATA_BASE = "https://data-api.polymarket.com"
CLOB_BASE = "https://clob.polymarket.com"

def get_active_markets(limit: int = 50, min_volume: float = 10000) -> pd.DataFrame:
    """Fetch clean, parsed active markets with prices & sentiment signals."""
    url = f"{GAMMA_BASE}/markets"
    params = {"active": "true", "limit": limit}
    
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()                    # ← direct list (confirmed)
    
    df = pd.DataFrame(data)
    if df.empty:
        return df
    
    # Filter
    df = df[(df['active'] == True) & (~df.get('closed', False))]
    
    # Parse JSON strings
    def safe_json(x):
        if isinstance(x, str) and x.startswith('['):
            try: return json.loads(x)
            except: return []
        return x if isinstance(x, list) else []
    
    df['clobTokenIds'] = df['clobTokenIds'].apply(safe_json)
    df['outcomePrices'] = df['outcomePrices'].apply(safe_json)
    
    # Yes probability (first outcome = Yes in most markets)
    df['yes_price'] = df['outcomePrices'].apply(lambda x: float(x[0]) if len(x) > 0 else 0.5)
    
    # Numeric columns
    numeric_cols = ['volume', 'liquidity', 'volumeNum', 'liquidityNum', 
                    'oneDayPriceChange', 'oneHourPriceChange']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Volume filter + sort
    if 'volumeNum' in df.columns:
        df = df[df['volumeNum'] >= min_volume]
    df = df.sort_values('volumeNum', ascending=False)
    
    return df

def get_trades(condition_id: str, limit: int = 5) -> pd.DataFrame:
    url = f"{DATA_BASE}/trades"
    params = {"market": condition_id, "limit": limit}
    r = requests.get(url, params=params)
    r.raise_for_status()
    return pd.DataFrame(r.json())

def get_midpoint(token_id: str) -> float:
    """Fallback live price from CLOB."""
    if not token_id:
        return 0.5
    try:
        client = ClobClient(CLOB_BASE)
        res = client.get_midpoint(token_id)
        return float(res.get("mid_price", 0.5))
    except:
        return 0.5
