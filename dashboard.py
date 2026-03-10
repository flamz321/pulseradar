import sys
import os

# Add src/agents/ to sys.path (only agents/ remains nested)
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'agents'))
if agents_dir not in sys.path:
    sys.path.insert(0, agents_dir)

print("Agents dir added to sys.path:", agents_dir)
print("Current working dir:", os.getcwd())

# Flat imports from root
from fetcher import get_active_markets
from sentiment import calculate_sentiment_score, get_category_indices
from crew import run_pulse_crew  # from src/agents/crew.py (after path add)

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

# Load data
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
    indices_df = get_category_indices(df)
    
    if not indices_df.empty:
        # Style the dataframe for better visualization
        styled_df = indices_df.style.format({
            'Sentiment Score': '{:.3f}',
            'Market Count': '{:.0f}'
        }).background_gradient(
            subset=['Sentiment Score'], 
            cmap='RdYlGn', 
            vmin=0, 
            vmax=1
        )
        
        st.dataframe(
            styled_df, 
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": "Category",
                "Sentiment Score": st.column_config.NumberColumn(
                    "Sentiment Score",
                    format="%.3f",
                    help="0 = Bearish, 1 = Bullish"
                ),
                "Market Count": "Markets",
                "Total Volume": "Total Volume"
            }
        )
        
        # Add a simple bar chart of sentiment scores
        fig = px.bar(
            indices_df[indices_df['Category'] != 'OVERALL'],
            x='Category',
            y='Sentiment Score',
            color='Sentiment Score',
            color_continuous_scale='RdYlGn',
            range_color=[0, 1],
            title="Sentiment Scores by Category",
            height=400
        )
        fig.add_hline(y=0.5, line_dash="dash", line_color="gray", 
                     annotation_text="Neutral")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category data available in current fetch.")

with tab3:
    st.subheader("🤖 Predictive Oracle Chat")
    
    # Check for API key in both os.environ and st.secrets
    has_openai = any([
        os.getenv("OPENAI_API_KEY"),
        st.secrets.get("OPENAI_API_KEY") if hasattr(st, "secrets") else None
    ])
    
    has_anthropic = any([
        os.getenv("ANTHROPIC_API_KEY"),
        st.secrets.get("ANTHROPIC_API_KEY") if hasattr(st, "secrets") else None
    ])
    
    has_groq = any([
        os.getenv("GROQ_API_KEY"),
        st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") else None
    ])
    
    if not (has_openai or has_anthropic or has_groq):
        st.warning(
            "⚠️ **No API keys found!**\n\n"
            "To use the Predictive Oracle, you need to add an API key in "
            "Streamlit Cloud Secrets:\n"
            "1. Go to your app settings\n"
            "2. Click on 'Secrets'\n"
            "3. Add: `OPENAI_API_KEY = \"sk-...\"`\n\n"
            "The dashboard will still show live markets without the Oracle."
        )
    else:
        st.info("💡 Ask anything (e.g., 'Predict Fed rate reaction', 'What's moving in crypto?')")
        
        if prompt := st.chat_input("Ask the Oracle..."):
            with st.spinner("🧠 Analyzing markets and scanning internet signals..."):
                try:
                    report = run_pulse_crew(prompt)
                    st.markdown(report)
                except Exception as e:
                    st.error(f"Prediction error: {str(e)}")
                    st.info("This might be an API key issue. Check your Streamlit secrets.")
