from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import os

# Absolute import from same folder (tools.py)
from tools import get_top_movers, scan_external_signals, predict_market_reaction, analyze_specific_market

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))

oracle = Agent(
    role="PulseRadar Oracle",
    goal="Forecast market moves using real-money data + internet signals",
    backstory="Elite forecaster correlating sentiment and trades.",
    tools=[get_top_movers, scan_external_signals, predict_market_reaction, analyze_specific_market],
    llm=llm,
    verbose=True
)

def run_pulse_crew(user_query: str) -> str:
    task = Task(
        description=f"PREDICT for '{user_query}'. Use tools. End with forecast.",
        agent=oracle,
        expected_output="Markdown report with prediction and confidence"
    )
    crew = Crew(agents=[oracle], tasks=[task], verbose=1)
    return crew.kickoff()
