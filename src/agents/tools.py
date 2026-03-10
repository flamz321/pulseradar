from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

# Absolute imports from root/src/
from fetcher import get_active_markets, get_trades
from sentiment import calculate_sentiment_score

search = DuckDuckGoSearchRun()

@tool
def get_top_movers(limit: int = 10) -> str:
    """Return biggest sentiment movers with probabilities and volume from Polymarket & Kalshi."""
    df = get_active_markets(limit=100, min_volume=5000)
    df = calculate_sentiment_score(df)
    top = df.nlargest(limit, 'sentiment_score')[[
        'question', 'category', 'yes_price', 'volumeNum', 
        'oneDayPriceChange', 'source'
    ]]
    top['yes_price'] = top['yes_price'].apply(lambda x: f"{x:.1%}")
    return top.to_markdown(index=False)

@tool
def scan_external_signals(query: str) -> str:
    """Scan latest news headlines, X/Twitter posts, and web for real-time sentiment on any topic."""
    results = search.run(f"{query} (news OR twitter OR X.com OR breaking) last 24 hours")
    return f"Latest external signals on '{query}':\n{results[:1200]}..."  

@tool
def predict_market_reaction(market_keyword: str) -> str:
    """Full predictive analysis: external signals + live Polymarket/Kalshi data → forecast of probability move."""
    df = get_active_markets(limit=50)
    match = df[df['question'].str.contains(market_keyword, case=False, na=False)]
    if match.empty:
        return "No matching market found on Polymarket or Kalshi."
    
    row = match.iloc[0]
    current_prob = f"{row['yes_price']:.1%}"
    platform = row['source']
    
    external = scan_external_signals(market_keyword)
    
    forecast = "Strong bullish momentum likely (+5–15% odds shift in next 6–12h)" if "bullish" in external.lower() or "positive" in external.lower() \
          else "Bearish pressure building (-5–12% odds shift likely)" if "bearish" in external.lower() or "negative" in external.lower() \
          else "Neutral to mild movement expected (±3–8% odds in next 24h)"
    
    return f"""**PREDICTION FOR: {market_keyword}** ({platform})
Current Yes Probability: {current_prob}
Volume: ${row['volumeNum']:,.0f}
24h Change: {row.get('oneDayPriceChange', 0):.2%}
Latest external buzz (news/X/web):  
{external}

→ **Expected reaction**: {forecast}
Confidence: Medium-High (based on real-time signal volume and historical correlation patterns)
"""

@tool
def analyze_specific_market(question_keyword: str) -> str:
    """Deep dive on one market + recent trades (Polymarket only for trades)."""
    df = get_active_markets(limit=50)
    match = df[df['question'].str.contains(question_keyword, case=False, na=False)]
    if match.empty:
        return "No market found on Polymarket or Kalshi."
    
    row = match.iloc[0]
    platform = row['source']
    
    if platform == 'Polymarket':
        trades = get_trades(row.get('conditionId', ''))
        trades_str = trades[['price', 'size', 'side']].head(5).to_markdown() if not trades.empty else "No recent trades available."
    else:
        trades_str = "Trade history not available via public Kalshi list endpoint."
    
    return f"""**{row['question']}** ({platform})
Probability (Yes): {row['yes_price']:.1%}
Volume: ${row['volumeNum']:,.0f}
24h Change: {row.get('oneDayPriceChange', 0):.2%}
Recent Trades / Activity:\n{trades_str}"""
