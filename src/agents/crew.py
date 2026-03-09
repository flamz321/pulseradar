from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from .tools import get_top_movers, analyze_specific_market
from .prompts import ANALYST_SYSTEM_PROMPT
import os

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, api_key=os.getenv("OPENAI_API_KEY"))

analyst = Agent(
    role="PolyPulse Senior Analyst",
    goal="Turn live Polymarket trading activity into clear global sentiment insights",
    backstory=ANALYST_SYSTEM_PROMPT,
    tools=[get_top_movers, analyze_specific_market],
    llm=llm,
    verbose=True
)

def run_pulse_crew(user_query: str) -> str:
    task = Task(
        description=f"Analyze current data and answer: {user_query}. "
                    "Use tools aggressively. Be concise and insightful.",
        agent=analyst,
        expected_output="Professional markdown report with bullets, tables, and a final Pulse rating."
    )
    crew = Crew(agents=[analyst], tasks=[task], verbose=1)
    return crew.kickoff()
