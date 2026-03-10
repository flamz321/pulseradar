import requests
import pandas as pd

def get_polymarket_markets(limit=50):
    """Fetch active markets from Polymarket"""
    url = "https://gamma-api.polymarket.com/markets"
    params = {
        "active": "true",
        "closed": "false",
        "limit": limit,
        "order": "volume",
        "ascending": "false"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        markets = response.json()
        
        data = []
        for m in markets:
            data.append({
                'question': m.get('question', 'N/A'),
                'category': m.get('category', 'Other'),
                'yes_price': float(m.get('yes_bid', 0.5)),
                'volume': float(m.get('volume', 0)),
                'source': 'Polymarket',
                'condition_id': m.get('condition_id', '')
            })
        
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error fetching Polymarket: {e}")
        return pd.DataFrame()

def get_kalshi_markets(limit=50):
    """Placeholder for Kalshi (add later)"""
    return pd.DataFrame()

def get_all_markets(limit=50):
    """Combine all markets"""
    poly_df = get_polymarket_markets(limit)
    # kalshi_df = get_kalshi_markets(limit)  # Add later
    return poly_df  # Just Polymarket for now
