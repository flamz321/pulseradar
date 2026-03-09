import streamlit as st
import plotly.express as px
import os
from src.fetcher import get_active_markets
from src.sentiment import calculate_sentiment_score, get_category_indices
from src.agents.crew import run_pulse_crew

st.set_page_config(page_title="PolyPulse", page_icon="💓", layout="wide")
st.title("🌍 PolyPulse")
st.caption("Real-time global sentiment from Polymarket real-money trades • Skin in the game > polls")

# Controls
st.sidebar.header("Controls")
refresh = st.sidebar.button("🔄 Refresh Live Data")
limit = st.sidebar.slider("Markets to show", 10, 100, 30)
min_vol = st.sidebar.number_input("Min volume ($)", 1000, 1000000, 25000, step=10000)

if refresh or 'df' not in st.session_state:
    with st.spinner("Fetching live markets from Polymarket..."):
        raw = get_active_markets(limit=limit * 2, min_volume=min_vol)
        df = calculate_sentiment_score(raw)
        st.session_state.df = df

df = st.session_state.get('df', None)
if df is None or df.empty:
    st.error("No markets found — try lowering min volume")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📊 Live Markets", "📈 Category Indices", "🤖 AI Analyst"])

with tab1:
    st.subheader("Top Markets")
    show = df[['question', 'category', 'yes_price', 'volumeNum', 'liquidityNum', 'oneDayPriceChange']].copy()
    show['yes_price'] = show['yes_price'].apply(lambda x: f"{x:.1%}")
    st.dataframe(show, use_container_width=True, hide_index=True)
    
    fig = px.bar(df.head(10), x='question', y='volumeNum', title="Top 10 by Volume", text='volumeNum')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Global Sentiment by Category")
    indices = get_category_indices(df)
    st.dataframe(indices, use_container_width=True)

with tab3:
    st.subheader("🤖 PolyPulse AI Analyst")
    if not os.getenv("OPENAI_API_KEY"):
        st.info("Add your OpenAI key to `.env` to unlock the AI agent")
    else:
        if prompt := st.chat_input("Ask anything — e.g. 'Biggest movers today?' or 'Crypto sentiment?'"):
            with st.spinner("Agents analyzing live trades..."):
                report = run_pulse_crew(prompt)
                st.markdown(report)
