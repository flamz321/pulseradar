import pandas as pd
import numpy as np
from datetime import datetime

def calculate_sentiment_score(df):
    """
    Calculate sentiment score based on volume, price movement, and market activity
    """
    if df.empty:
        return df
    
    # Create a copy to avoid warnings
    df = df.copy()
    
    # Normalize volume (0-1 scale)
    if 'volumeNum' in df.columns and not df['volumeNum'].isnull().all():
        max_volume = df['volumeNum'].max()
        if max_volume > 0:
            df['volume_score'] = df['volumeNum'] / max_volume
        else:
            df['volume_score'] = 0
    else:
        df['volume_score'] = 0
    
    # Price momentum score
    if 'oneDayPriceChange' in df.columns:
        # Clip extreme values to avoid outliers
        df['price_change_score'] = df['oneDayPriceChange'].clip(-0.5, 0.5) + 0.5
        df['price_change_score'] = df['price_change_score'] / df['price_change_score'].max() if df['price_change_score'].max() > 0 else 0
    else:
        df['price_change_score'] = 0.5
    
    # Yes price score (higher price = more confidence)
    if 'yes_price' in df.columns:
        df['price_level_score'] = df['yes_price']
    else:
        df['price_level_score'] = 0.5
    
    # Combine scores (customize weights as needed)
    df['sentiment_score'] = (
        df['volume_score'] * 0.4 + 
        df['price_change_score'] * 0.3 + 
        df['price_level_score'] * 0.3
    )
    
    return df

def get_sentiment_trend(market_history):
    """
    Analyze sentiment trend over time
    """
    if market_history.empty:
        return "neutral", 0
    
    recent = market_history.tail(10)
    if len(recent) < 3:
        return "neutral", 0
    
    # Calculate trend
    price_changes = recent['yes_price'].pct_change().dropna()
    avg_change = price_changes.mean()
    
    if avg_change > 0.02:
        trend = "bullish"
    elif avg_change < -0.02:
        trend = "bearish"
    else:
        trend = "neutral"
    
    return trend, avg_change
