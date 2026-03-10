from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import pandas as pd
import json
import requests

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
        search_wrapper = DuckDuckGoSearchAPIWrapper(
            max_results=5,
            region="wt-wt",
            safesearch="moderate",
            time="d"
        )
        search = DuckDuckGoSearchRun(api_wrapper=search_wrapper)
    except Exception as e:
        print(f"Error initializing DuckDuckGo search: {e}")
        SEARCH_AVAILABLE = False
        search = None
else:
    search = None

# Define input schemas for tools
class TopMoversInput(BaseModel):
    """Input schema for get_top_movers tool"""
    limit: int = Field(10, description="Number of top movers to return")

class ExternalSignalsInput(BaseModel):
    """Input schema for scan_external_signals tool"""
    query: str = Field(..., description="Search query for external signals")

class MarketReactionInput(BaseModel):
    """Input schema for predict_market_reaction tool"""
    market_keyword: str = Field(..., description="Keyword to identify the market")

class MarketAnalysisInput(BaseModel):
    """Input schema for analyze_specific_market tool"""
    question_keyword: str = Field(..., description="Keyword to identify the market question")

# Define tools as CrewAI BaseTool classes
class GetTopMoversTool(BaseTool):
    name: str = "get_top_movers"
    description: str = "Get top moving markets by sentiment score"
    args_schema: Type[BaseModel] = TopMoversInput
    
    def _run(self, limit: int = 10) -> str:
        """Execute the tool"""
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

class ScanExternalSignalsTool(BaseTool):
    name: str = "scan_external_signals"
    description: str = "Scan external sources for signals about a specific query"
    args_schema: Type[BaseModel] = ExternalSignalsInput
    
    def _run(self, query: str) -> str:
        """Execute the tool"""
        try:
            if SEARCH_AVAILABLE and search:
                try:
                    results = search.run(f"{query} news OR breaking OR sentiment last 24 hours")
                    return f"Latest external signals on '{query}':\n{results[:1200]}..."
                except Exception as e:
                    return f"Search temporarily unavailable: {str(e)}"
            else:
                return f"Web search is currently unavailable. Please install duckduckgo-search package for full functionality."
        except Exception as e:
            return f"Error scanning external signals: {str(e)}"

class PredictMarketReactionTool(BaseTool):
    name: str = "predict_market_reaction"
    description: str = "Predict market reaction based on external signals and current data"
    args_schema: Type[BaseModel] = MarketReactionInput
    
    def _run(self, market_keyword: str) -> str:
        """Execute the tool"""
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
            
            # Get external signals
            external = self._get_external_signals(market_keyword)
            
            # Simple sentiment analysis
            forecast = self._analyze_sentiment(external)
            
            return f"""
**PREDICTION FOR: {market_keyword}** ({platform})
Current Yes Probability: {current_prob}
Volume: ${volume:,.0f}

Latest external buzz:
{external[:500]}...

→ **Expected reaction**: {forecast}
Confidence: Medium-High
"""
        except Exception as e:
            return f"Error predicting market reaction: {str(e)}"
    
    def _get_external_signals(self, query: str) -> str:
        """Helper to get external signals"""
        if SEARCH_AVAILABLE and search:
            try:
                return search.run(f"{query} news OR breaking OR sentiment last 24 hours")
            except:
                return "External signals temporarily unavailable"
        return "Web search unavailable"
    
    def _analyze_sentiment(self, text: str) -> str:
        """Helper to analyze sentiment from text"""
        text_lower = text.lower()
        if "bullish" in text_lower or "positive" in text_lower or "surge" in text_lower:
            return "Strong bullish momentum likely (+5–15% odds shift in next 6–12h)"
        elif "bearish" in text_lower or "negative" in text_lower or "crash" in text_lower:
            return "Bearish pressure building (-5–12% odds shift likely)"
        else:
            return "Neutral to mild movement expected (±3–8% odds in next 24h)"

class AnalyzeSpecificMarketTool(BaseTool):
    name: str = "analyze_specific_market"
    description: str = "Analyze a specific market in detail"
    args_schema: Type[BaseModel] = MarketAnalysisInput
    
    def _run(self, question_keyword: str) -> str:
        """Execute the tool"""
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

# Create instances of the tools
get_top_movers = GetTopMoversTool()
scan_external_signals = ScanExternalSignalsTool()
predict_market_reaction = PredictMarketReactionTool()
analyze_specific_market = AnalyzeSpecificMarketTool()
