from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import os

# No relative import – use absolute from same folder
from tools import get_top_movers, scan_external_signals, predict_market_reaction, analyze_specific_market

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)

oracle = Agent(
    role="PulseRadar Predictive Oracle",
    goal="Combine live real-money data from Polymarket and Kalshi with real-time social/news signals to forecast how prediction markets will move",
    backstory=(
        "You are an elite prediction-market forecaster. "
        "You correlate external sentiment spikes (news, X/Twitter, web buzz) "
        "with actual trading flow and probabilities from Polymarket and Kalshi "
        "to predict probability shifts with high conviction."
    ),
    tools=[get_top_movers, scan_external_signals, predict_market_reaction, analyze_specific_market],
    llm=llm,
    verbose=True,
    allow_delegation=False
)

def run_pulse_crew(user_query: str) -> str:
    task = Task(
        description=(
            f"Analyze and PREDICT market reaction for: '{user_query}'. "
            "Use external signal scanning + live Polymarket/Kalshi data. "
            "Always include: current probabilities, key external signals, "
            "reasoning, and a clear forecast of expected odds move with timeframe."
        ),
        agent=oracle,
        expected_output=(
            "Professional markdown report including:\n"
            "- Market(s) matched\n"
            "- Current probabilities and platform\n"
            "- Summary of latest external buzz\n"
            "- Reasoning and correlation\n"
            "- Final forecast: 'Expected Move: +X% / -Y% in Z hours' with confidence"
        )
    )

    crew = Crew(
        agents=[oracle],
        tasks=[task],
        verbose=1
    )

    result = crew.kickoff()
    return result
