from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os
import streamlit as st

# Import tool instances
from tools import (
    get_top_movers, 
    scan_external_signals, 
    predict_market_reaction, 
    analyze_specific_market
)

# Check for API key with better error handling
api_key = os.getenv("OPENAI_API_KEY")

# If running on Streamlit Cloud, also check st.secrets
if not api_key:
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except:
        api_key = None

if not api_key:
    raise ValueError(
        "OpenAI API key not found! Please set OPENAI_API_KEY in your "
        "Streamlit Cloud secrets (Settings → Secrets) or in your .env file."
    )

try:
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0.3, 
        api_key=api_key,
        max_retries=2,
        timeout=60
    )
except Exception as e:
    st.error(f"Failed to initialize OpenAI: {str(e)}")
    raise

# Create the agent with the tools
oracle = Agent(
    role="PulseRadar Oracle",
    goal="Forecast market moves using real-money data + internet signals",
    backstory="""You are an elite forecaster who correlates real-money trading activity 
    with internet sentiment to predict market movements. You have access to Polymarket 
    and Kalshi data, and you scan social media and news for signals.""",
    tools=[
        get_top_movers,
        scan_external_signals,
        predict_market_reaction,
        analyze_specific_market
    ],
    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=5,
    max_rpm=10
)

def run_pulse_crew(user_query: str) -> str:
    """Run the crew with the user query"""
    try:
        task = Task(
            description=f"""
            Analyze and predict market movements based on: '{user_query}'
            
            Use your tools to:
            1. Check current market data and sentiment
            2. Scan external signals (news, social media)
            3. Analyze specific relevant markets
            4. Provide a clear prediction with confidence level
            
            Format your response as a markdown report with sections.
            """,
            agent=oracle,
            expected_output="A detailed markdown report with market analysis and prediction"
        )
        
        crew = Crew(
            agents=[oracle],
            tasks=[task],
            verbose=1,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return str(result)
        
    except Exception as e:
        return f"Error during prediction: {str(e)}"
