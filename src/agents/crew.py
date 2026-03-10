from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import os
import streamlit as st

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

# Absolute import from same folder (tools.py)
from tools import get_top_movers, scan_external_signals, predict_market_reaction, analyze_specific_market

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

oracle = Agent(
    role="PulseRadar Oracle",
    goal="Forecast market moves using real-money data + internet signals",
    backstory="Elite forecaster correlating sentiment and trades.",
    tools=[get_top_movers, scan_external_signals, predict_market_reaction, analyze_specific_market],
    llm=llm,
    verbose=True,
    allow_delegation=False
)

def run_pulse_crew(user_query: str) -> str:
    """Run the crew with the user query"""
    try:
        task = Task(
            description=f"PREDICT for '{user_query}'. Use tools. End with forecast.",
            agent=oracle,
            expected_output="Markdown report with prediction and confidence"
        )
        crew = Crew(
            agents=[oracle], 
            tasks=[task], 
            verbose=1,
            process="sequential"
        )
        result = crew.kickoff()
        return str(result)  # Ensure we return a string
    except Exception as e:
        return f"Error during prediction: {str(e)}"
