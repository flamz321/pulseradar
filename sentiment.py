import pandas as pd
import numpy as np

def calculate_sentiment(df):
    """Calculate simple sentiment scores"""
    if df.empty:
        return df
    
    df = df.copy()
    
    # Normalize volume (0-1)
    if not df['volume'].empty and df['volume'].max() > 0:
        df['volume_score'] = df['volume'] / df['volume'].max()
    else:
        df['volume_score'] = 0
    
    # Yes price is already 0-1
    df['price_score'] = df['yes_price']
    
    # Simple sentiment = volume * 0.5 + price * 0.5
    df['sentiment'] = (df['volume_score'] * 0.5 + df['price_score'] * 0.5)
    
    return df

def get_category_sentiment(df):
    """Aggregate sentiment by category"""
    if df.empty:
        return pd.DataFrame()
    
    categories = ['Politics', 'Crypto', 'Macro', 'Geopolitics', 'Culture']
    results = []
    
    for cat in categories:
        cat_df = df[df['category'] == cat]
        if not cat_df.empty:
            results.append({
                'Category': cat,
                'Sentiment': cat_df['sentiment'].mean(),
                'Markets': len(cat_df),
                'Volume': f"${cat_df['volume'].sum():,.0f}"
            })
    
    # Add overall
    if not df.empty:
        results.append({
            'Category': 'OVERALL',
            'Sentiment': df['sentiment'].mean(),
            'Markets': len(df),
            'Volume': f"${df['volume'].sum():,.0f}"
        })
    
    return pd.DataFrame(results)
