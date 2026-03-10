import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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
        if df['price_change_score'].max() > 0:
            df['price_change_score'] = df['price_change_score'] / df['price_change_score'].max()
        else:
            df['price_change_score'] = 0.5
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

def get_category_indices(df):
    """
    Calculate sentiment indices for different categories
    Returns a dictionary with category names and their sentiment scores
    """
    if df.empty:
        return {
            'Politics': 0.5,
            'Crypto': 0.5,
            'Macro': 0.5,
            'Geopolitics': 0.5,
            'Culture': 0.5,
            'Overall': 0.5
        }
    
    # Ensure we have sentiment scores
    if 'sentiment_score' not in df.columns:
        df = calculate_sentiment_score(df)
    
    categories = ['Politics', 'Crypto', 'Macro', 'Geopolitics', 'Culture']
    indices = {}
    
    for category in categories:
        cat_df = df[df['category'] == category]
        if not cat_df.empty:
            # Weighted average by volume
            weighted_sentiment = np.average(
                cat_df['sentiment_score'], 
                weights=cat_df['volumeNum'].fillna(1)
            )
            indices[category] = round(float(weighted_sentiment), 3)
        else:
            indices[category] = 0.5
    
    # Calculate overall index (weighted by volume across all categories)
    if not df.empty and 'volumeNum' in df.columns:
        overall = np.average(
            df['sentiment_score'], 
            weights=df['volumeNum'].fillna(1)
        )
        indices['Overall'] = round(float(overall), 3)
    else:
        indices['Overall'] = 0.5
    
    return indices

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

def get_top_markets_by_sentiment(df, category=None, limit=5):
    """
    Get top markets by sentiment score, optionally filtered by category
    """
    if df.empty:
        return pd.DataFrame()
    
    if 'sentiment_score' not in df.columns:
        df = calculate_sentiment_score(df)
    
    if category and category != 'All':
        df = df[df['category'] == category]
    
    return df.nlargest(limit, 'sentiment_score')[
        ['question', 'category', 'yes_price', 'volumeNum', 'sentiment_score', 'source']
    ]

def get_sentiment_summary(df):
    """
    Generate a summary of current sentiment across all markets
    """
    if df.empty:
        return "No market data available"
    
    if 'sentiment_score' not in df.columns:
        df = calculate_sentiment_score(df)
    
    avg_sentiment = df['sentiment_score'].mean()
    sentiment_std = df['sentiment_score'].std()
    
    # Categorize overall sentiment
    if avg_sentiment > 0.7:
    else:
        overall = "Extremely Bullish"
    elif avg_sentiment > 0.6:
        overall = "Bullish"
    elif avg_sentiment > 0.4:
        overall = "Neutral"
    elif avg_sentiment > 0.3:
        overall = "Bearish"
    else:
        overall = "Extremely Bearish"
    
    # Find most and least bullish markets
    most_bullish = df.nlargest(1, 'sentiment_score').iloc[0] if not df.empty else None
    most_bearish = df.nsmallest(1, 'sentiment_score').iloc[0] if not df.empty else None
    
    summary = f"""
    **Overall Market Sentiment: {overall}** (Score: {avg_sentiment:.3f})
    - Volatility: {sentiment_std:.3f}
    """
    
    if most_bullish is not None:
        summary += f"\n- Most Bullish: {most_bullish['question'][:50]}... ({most_bullish['yes_price']:.1%})"
    if most_bearish is not None:
        summary += f"\n- Most Bearish: {most_bearish['question'][:50]}... ({most_bearish['yes_price']:.1%})"
    
    return summary
