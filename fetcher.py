import pandas as pd
import requests
import os
from datetime import datetime, timedelta

def get_active_markets(limit=100, min_volume=5000):
    """
    Fetch active markets from Polymarket and Kalshi
    """
    all_markets = []
    
    # Polymarket markets
    try:
        poly_url = "https://gamma-api.polymarket.com/markets"
        poly_params = {
            "active": "true",
            "closed": "false",
            "limit": limit,
            "order": "volume",
            "ascending": "false"
        }
        poly_response = requests.get(poly_url, params=poly_params)
        if poly_response.status_code == 200:
            poly_markets = poly_response.json()
            for market in poly_markets:
                if float(market.get('volume', 0)) >= min_volume:
                    all_markets.append({
                        'question': market.get('question', ''),
                        'category': market.get('category', 'Other'),
                        'yes_price': float(market.get('yes_bid', 0)) if market.get('yes_bid') else 0.5,
                        'volume': market.get('volume', '0'),
                        'volumeNum': float(market.get('volume', 0)),
                        'source': 'Polymarket',
                        'conditionId': market.get('condition_id', ''),
                        'oneDayPriceChange': float(market.get('price_change_24h', 0)) if market.get('price_change_24h') else 0
                    })
    except Exception as e:
        print(f"Error fetching Polymarket: {e}")
    
    # Kalshi markets (placeholder - implement based on their API)
    try:
        # Add Kalshi API integration here
        pass
    except Exception as e:
        print(f"Error fetching Kalshi: {e}")
    
    df = pd.DataFrame(all_markets)
    if not df.empty:
        df = df.nlargest(limit, 'volumeNum')
    
    return df

def get_trades(condition_id, limit=10):
    """
    Fetch recent trades for a specific Polymarket market
    """
    try:
        trades_url = f"https://gamma-api.polymarket.com/trades"
        params = {
            "condition_id": condition_id,
            "limit": limit,
            "order": "created_at",
            "ascending": "false"
        }
        response = requests.get(trades_url, params=params)
        if response.status_code == 200:
            trades = response.json()
            trades_data = []
            for trade in trades:
                trades_data.append({
                    'price': float(trade.get('price', 0)),
                    'size': float(trade.get('size', 0)),
                    'side': trade.get('side', 'unknown'),
                    'timestamp': trade.get('created_at', '')
                })
            return pd.DataFrame(trades_data)
    except Exception as e:
        print(f"Error fetching trades: {e}")
    
    return pd.DataFrame(columns=['price', 'size', 'side', 'timestamp'])

def get_market_details(market_id):
    """
    Get detailed information about a specific market
    """
    try:
        url = f"https://gamma-api.polymarket.com/markets/{market_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching market details: {e}")
    return None
