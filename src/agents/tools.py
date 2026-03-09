from langchain.tools import tool
from src.fetcher import get_active_markets, get_market_price
import pandas as pd

@tool
def get_top_movers(limit: int = 10) -> str:
    """Returns the biggest price/volume movers in the last 24h."""
    df = get_active_markets(limit=100)
    # simple mock sentiment score — replace with your real logic
    df["sentiment_score"] = (df.get("price", 0.5) - 0.5) * df.get("volume", 0)
    movers = df.nlargest(limit, "sentiment_score")[["question", "volume", "sentiment_score"]]
    return movers.to_markdown()

@tool
def analyze_market(question: str) -> str:
    """Fetch latest price, volume, and trades for a specific market question."""
    # fuzzy match or search logic here
    df = get_active_markets(limit=50)
    match = df[df["question"].str.contains(question, case=False)].iloc[0]
    price = get_market_price(match["token_id"])  # assuming you have token_id
    return f"Market: {match['question']}\nProbability: {price}\nVolume: {match.get('volume')}"
