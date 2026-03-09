from langchain.tools import tool
from src.fetcher import get_active_markets, get_trades
from src.sentiment import calculate_sentiment_score

@tool
def get_top_movers(limit: int = 10) -> str:
    """Return biggest sentiment movers with probabilities and volume."""
    df = get_active_markets(limit=100, min_volume=5000)
    df = calculate_sentiment_score(df)
    top = df.nlargest(limit, 'sentiment_score')[[
        'question', 'category', 'yes_price', 'volumeNum', 
        'oneDayPriceChange', 'sentiment_score'
    ]]
    top['yes_price'] = top['yes_price'].apply(lambda x: f"{x:.1%}")
    return top.to_markdown(index=False)

@tool
def analyze_specific_market(question_keyword: str) -> str:
    """Deep dive on one market + recent trades."""
    df = get_active_markets(limit=50)
    match = df[df['question'].str.contains(question_keyword, case=False, na=False)]
    if match.empty:
        return "No market found."
    
    row = match.iloc[0]
    trades = get_trades(row.get('conditionId', ''))
    trades_str = trades[['price', 'size', 'side']].head(5).to_markdown() if not trades.empty else "No recent trades."
    
    return f"""**{row['question']}**
Probability (Yes): {row['yes_price']:.1%}
Volume: ${row['volumeNum']:,.0f}
24h Change: {row.get('oneDayPriceChange', 0):.2%}
Recent Trades:\n{trades_str}"""
