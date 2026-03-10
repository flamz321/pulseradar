import sys
import os

# Add src/agents/ to sys.path (only agents/ remains nested)
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'agents'))
if agents_dir not in sys.path:
    sys.path.insert(0, agents_dir)

print("Agents dir added to sys.path:", agents_dir)
print("Current working dir:", os.getcwd())

# Root-level imports (fetcher & sentiment are now in root)
from fetcher import get_active_markets
from sentiment import calculate_sentiment_score, get_category_indices
from crew import run_pulse_crew  # from src/agents/crew.py

import streamlit as st
import plotly.express as px

st.set_page_config(page_title="PulseRadar", page_icon="📡", layout="wide")

st.title("🌍 PulseRadar")
st.caption("AI Predictive Sentiment Radar • Polymarket + Kalshi • Scans social/news to predict moves")

# Sidebar
st.sidebar.header("Controls")
refresh = st.sidebar.button("🔄 Refresh Live Data")
limit = st.sidebar.slider("Markets to show", 10, 150, 50)
min_vol = st.sidebar.number_input("Min volume ($)", 1000, 1000000, 25000, step=5000)

# Load data
if refresh or 'df' not in st.session_state:
    with st.spinner("Fetching live markets..."):
        raw = get_active_markets(limit=limit * 2, min_volume=min_vol)
        df = calculate_sentiment_score(raw)
        st.session_state.df = df

df = st.session_state.get('df', None)
if df is None or df.empty:
    st.error("No markets found — lower min volume?")
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Live Markets", "📈 Indices", "🤖 Oracle"])

with tab1:
    st.subheader("Live Markets")
    show = df[['question', 'source', 'yes_price', 'volumeNum', 'oneDayPriceChange', 'category']].copy()
    show['yes_price'] = show['yes_price'].apply(lambda x: f"{x:.1%}")
    st.dataframe(show.rename(columns={'yes_price': 'Yes %', 'volumeNum': 'Vol $', 'oneDayPriceChange': '24h Δ'}), use_container_width=True, hide_index=True)

    fig = px.bar(df.head(12), x='question', y='volumeNum', color='source', title="Top Volume", height=500)
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Sentiment by Category")
    indices = get_category_indices(df)
    if not indices.empty:
        st.dataframe(indices, use_container_width=True)
    else:
        st.info("No category data.")

with tab3:
    st.subheader("Predictive Oracle")
    if not any(os.getenv(k) for k in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GROQ_API_KEY"]):
        st.warning("Add LLM API key in Secrets to enable Oracle.")
    else:
        st.info("Ask anything (e.g. 'Predict Fed rate reaction')")
        if prompt := st.chat_input("Ask Oracle..."):
            with st.spinner("Analyzing..."):
                try:
                    report = run_pulse_crew(prompt)
                    st.markdown(report)
                except Exception as e:
                    st.error(f"Prediction error: {str(e)}")
