import sys
import os

# Explicitly add 'src/' folder to sys.path
# This fixes ModuleNotFoundError and SyntaxError on relative imports like 'agents.crew'
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Debug prints (visible in Streamlit logs – comment out later if you want)
print(f"Added src/ path: {src_path}")
print(f"sys.path now includes src: {'src' in ' '.join(sys.path)}")
print(f"Current working dir: {os.getcwd()}")

# Now import everything from src/ using absolute paths
from fetcher import get_active_markets
from sentiment import calculate_sentiment_score, get_category_indices
from agents.crew import run_pulse_crew

import streamlit as st
import plotly.express as px

# Page config
st.set_page_config(
    page_title="PulseRadar",
    page_icon="📡",
    layout="wide"
)

# Title & caption
st.title("🌍 PulseRadar")
st.caption(
    "AI Predictive Sentiment Radar • Polymarket + Kalshi • "
    "Scans social/news in real-time to forecast market moves"
)

# Sidebar controls
st.sidebar.header("Controls")
refresh = st.sidebar.button("🔄 Refresh Live Data")
limit = st.sidebar.slider("Markets to show", 10, 150, 50)
min_vol = st.sidebar.number_input("Min volume ($)", 1000, 1000000, 25000, step=5000)

# Load data (cached in session state)
if refresh or 'df' not in st.session_state:
    with st.spinner("Fetching live markets from Polymarket & Kalshi..."):
        raw = get_active_markets(limit=limit * 2, min_volume=min_vol)
        df = calculate_sentiment_score(raw)
        st.session_state.df = df

df = st.session_state.get('df', None)
if df is None or df.empty:
    st.error("No markets found — try lowering the min volume filter.")
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs([
    "📊 Live Markets",
    "📈 Category Indices",
    "🤖 Predictive Oracle"
])

with tab1:
    st.subheader("Combined Live Markets (Polymarket + Kalshi)")
    show_cols = [
        'question', 'source', 'yes_price', 'volumeNum',
        'oneDayPriceChange', 'category'
    ]
    display_df = df[show_cols].copy()
    display_df['yes_price'] = display_df['yes_price'].apply(lambda x: f"{x:.1%}")
    display_df = display_df.rename(columns={
        'yes_price': 'Yes Prob',
        'volumeNum': 'Volume ($)',
        'oneDayPriceChange': '24h Δ',
        'source': 'Platform'
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Top volume bar chart
    fig = px.bar(
        df.head(12),
        x='question',
        y='volumeNum',
        color='source',
        title="Top 12 Markets by Volume",
        text_auto=True,
        height=500
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Global Sentiment by Category")
    indices = get_category_indices(df)
    if not indices.empty:
        st.dataframe(indices, use_container_width=True)
    else:
        st.info("No category data available in current fetch.")

with tab3:
    st.subheader("🤖 Predictive Oracle Chat")
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("GROQ_API_KEY"):
        st.warning(
            "Add at least one LLM API key (OpenAI, Claude, Groq, etc.) "
            "to Streamlit Secrets to unlock the Predictive Oracle agents."
        )
    else:
        st.info(
            "Ask the Oracle anything — e.g.\n"
            "• Predict reaction to next Fed rate decision\n"
            "• How will Trump news affect 2028 odds?\n"
            "• What's the buzz around Bitcoin ETF markets?"
        )

        if prompt := st.chat_input("Ask the Oracle..."):
            with st.spinner("Scanning markets + external signals..."):
                try:
                    report = run_pulse_crew(prompt)
                    st.markdown(report)
                except Exception as e:
                    st.error(f"Error running prediction: {str(e)}")
                    st.info("Make sure your LLM API key is valid and you have internet access.")
