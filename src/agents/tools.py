from langchain.tools import tool
import pandas as pd
import json
import requests
from typing import Optional, Dict, Any

# Try to import DuckDuckGoSearch, but handle if it fails
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False
    print("Warning: DuckDuckGo search not available. Using fallback search.")

# Root-level imports
from fetcher import get_active_markets, get_trades
from sentiment import calculate_sentiment_score

# Initialize search with error handling
if SEARCH_AVAILABLE:
    try:
        # Configure search wrapper with proper parameters
        search_wrapper = DuckDuckGoSearchAPIWrapper(
            max_results=5,
            region="wt-wt",  # Worldwide
            safesearch="moderate",
            time="d"  # Last day
        )
        search = DuckDuckGoSearchRun(api_wrapper=search_wrapper)
    except Exception as e:
        print(f"Error initializing DuckDuckGo search: {e}")
        SEARCH_AVAILABLE = False
        search = None
else:
    search = None

def fallback_web_search(query: str) -> str:
    """
    Fallback search function using simple HTTP requests
    """
    try:
        # Use a simple news API or Google Custom Search as fallback
        # For now, return a placeholder
        return f"Search results for '{query}' would appear here. Please install duckduckgo-search package: pip install duckduckgo-search"
    except Exception as e:
        return f"Search unavailable: {str(e)}"

@tool
def get_top_movers(limit: int = 10) -> str:
    """Get top moving markets by sentiment score"""
    try:
        df = get_active_markets(limit=100, min_volume=5000)
        if df.empty:
            return "No markets available at this time."
        
        df = calculate_sentiment_score(df)
        top = df.nlargest(limit, 'sentiment_score')[['question', 'category', 'yes_price', 'volumeNum', 'source']]
        top['yes_price'] = top['yes_price'].apply(lambda x: f"{x:.1%}")
        top['volumeNum'] = top['volumeNum'].apply(lambda x: f"${x:,.0f}")
        return top.to_markdown(index=False)
    except Exception as e:
        return f"Error getting top movers: {str(e)}"

@tool
def scan_external_signals(query: str) -> str:
    """Scan external sources for signals about a specific query"""
    try:
        if SEARCH_AVAILABLE and search:
            # Try to use DuckDuckGo search
            try:
                results = search.run(f"{query} news OR breaking OR sentiment last 24 hours")
                return f"Latest external signals on '{query}':\n{results[:1200]}..."
            except Exception as e:
                print(f"DuckDuckGo search failed: {e}")
                return fallback_web_search(query)
        else:
            return fallback_web_search(query)
    except Exception as e:
        return f"Error scanning external signals: {str(e)}"

@tool
def predict_market_reaction(market_keyword: str) -> str:
    """Predict market reaction based on external signals and current data"""
    try:
        df = get_active_markets(limit=50)
        if df.empty:
            return "No markets available to analyze."
        
        match = df[df['question'].str.contains(market_keyword, case=False, na=False)]
        if match.empty:
            return f"No matching market found for '{market_keyword}'."
        
        row = match.iloc[0]
        current_prob = f"{row['yes_price']:.1%}"
        platform = row['source']
        volume = row.get('volumeNum', 0)
        
        external = scan_external_signals(market_keyword)
        
        # Simple sentiment analysis on external signals
        external_lower = external.lower()
        if "bullish" in external_lower or "positive" in external_lower or "surge" in external_lower:
            forecast = "Strong bullish momentum likely (+5–15% odds shift in next 6–12h)"
        elif "bearish" in external_lower or "negative" in external_lower or "crash" in external_lower:
            forecast = "Bearish pressure building (-5–12% odds shift likely)"
        else:
            forecast = "Neutral to mild movement expected (±3–8% odds in next 24h)"
        
        return f"""
**PREDICTION FOR: {market_keyword}** ({platform})
Current Yes Probability: {current_prob}
Volume: ${volume:,.0f}

Latest external buzz (news/X/web):  
{external[:500]}...

→ **Expected reaction**: {forecast}
Confidence: Medium-High
"""
    except Exception as e:
        return f"Error predicting market reaction: {str(e)}"

@tool
def analyze_specific_market(question_keyword: str) -> str:
    """Analyze a specific market in detail"""
    try:
        df = get_active_markets(limit=50)
        if df.empty:
            return "No markets available to analyze."
        
        match = df[df['question'].str.contains(question_keyword, case=False, na=False)]
        if match.empty:
            return f"No market found matching '{question_keyword}'."
        
        row = match.iloc[0]
        platform = row['source']
        
        # Get recent trades if available
        trades_str = "Trade history not available for this market."
        if platform == 'Polymarket' and 'conditionId' in row:
            trades = get_trades(row['conditionId'])
            if not trades.empty:
                trades['price'] = trades['price'].apply(lambda x: f"{x:.1%}")
                trades['size'] = trades['size'].apply(lambda x: f"{x:.4f}")
                trades_str = trades[['price', 'size', 'side']].head(5).to_markdown(index=False)
        
        return f"""
**{row['question']}** ({platform})
Probability (Yes): {row['yes_price']:.1%}
Volume: ${row.get('volumeNum', 0):,.0f}
24h Change: {row.get('oneDayPriceChange', 0):.2%}

Recent Trades / Activity:
{trades_str}
"""
    except Exception as e:
        return f"Error analyzing market: {str(e)}"
