from crewai import Agent, Task, Crew
from .tools import get_top_movers, analyze_market
from .prompts import ANALYST_PROMPT, ANOMALY_PROMPT

analyst = Agent(
    role="Polymarket Sentiment Analyst",
    goal="Turn raw market data into clear, actionable insights",
    backstory="You are an elite trader who only trusts real-money probabilities.",
    tools=[get_top_movers, analyze_market],
    verbose=True,
    llm="gpt-4o-mini"  # or "groq/llama3-70b" etc.
)

task = Task(
    description="Run a full sentiment sweep and highlight anything unusual.",
    agent=analyst,
    expected_output="Bullet-point report + alert recommendations"
)

def run_pulse_crew():
    crew = Crew(agents=[analyst], tasks=[task])
    result = crew.kickoff()
    return result
