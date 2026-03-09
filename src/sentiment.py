import pandas as pd

def calculate_sentiment_score(df: pd.DataFrame) -> pd.DataFrame:
    """Simple but powerful sentiment: price change × volume."""
    if df.empty:
        return df
    if 'oneDayPriceChange' in df.columns and 'volumeNum' in df.columns:
        df['sentiment_score'] = df['oneDayPriceChange'] * (df['volumeNum'] / 1000)
    else:
        df['sentiment_score'] = (df['yes_price'] - 0.5) * df['volumeNum']
    return df

def get_category_indices(df: pd.DataFrame) -> pd.DataFrame:
    """Global sentiment by category."""
    if df.empty or 'category' not in df.columns:
        return pd.DataFrame()
    return (df.groupby('category')
            .agg({'yes_price': 'mean', 'volumeNum': 'sum', 'sentiment_score': 'mean'})
            .round(4)
            .reset_index()
            .sort_values('volumeNum', ascending=False))
