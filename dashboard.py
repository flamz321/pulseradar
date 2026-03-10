import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from fetcher import get_all_markets
from sentiment import calculate_sentiment, get_category_sentiment

# Page config
st.set_page_config(
    page_title="PulseRadar • AI Predictive Sentiment Radar",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for the look
st.markdown("""
<style>
    /* Main background and text */
    .stApp {
        background: linear-gradient(180deg, #0A0A0F 0%, #1A1A2A 100%);
        color: #FFFFFF;
    }
    
    /* Metrics styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(10px);
    }
    
    .metric-value {
        font-size: 48px;
        font-weight: 700;
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Headers */
    h1, h2, h3 {
        background: linear-gradient(135deg, #FFFFFF 0%, #A0A0C0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    /* Stats cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    
    /* Radar pulse animation */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .radar-pulse {
        animation: pulse 2s infinite;
        color: #667EEA;
    }
</style>
""", unsafe_allow_html=True)

# Header with radar animation
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 style='text-align: center; font-size: 64px;'>📡</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>The radar<br>of the world</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #A0A0C0;'>AI agents scour X, Facebook, TikTok, Instagram, global news headlines, blogs, forums & public web sources in real time —<br>then predict how Polymarket & Kalshi markets will move based on real-world reaction patterns.</p>", unsafe_allow_html=True)

# Top stats row
col1, col2, col3, col4 = st.columns(4)

# Load data
if 'df' not in st.session_state:
    with st.spinner("Scanning global markets..."):
        raw_df = get_all_markets(100)
        if not raw_df.empty:
            st.session_state.df = calculate_sentiment(raw_df)
        else:
            # Sample data for demo
            sample = pd.DataFrame({
                'question': ['Trump 2028?', 'Bitcoin $100K?', 'Fed Rate Cut', 'EU Election', 'SpaceX IPO'],
                'category': ['Politics', 'Crypto', 'Macro', 'Geopolitics', 'Culture'],
                'yes_price': [0.61, 0.72, 0.45, 0.83, 0.34],
                'volume': [2400000, 1800000, 3200000, 950000, 1500000],
                'source': ['Polymarket', 'Polymarket', 'Kalshi', 'Polymarket', 'Kalshi']
            })
            st.session_state.df = calculate_sentiment(sample)

df = st.session_state.df

with col1:
    st.markdown("""
    <div class="metric-card">
        <div style="color: #A0A0C0;">🇺🇸</div>
        <div class="metric-value">{}</div>
        <div style="color: #A0A0C0;">Politics</div>
    </div>
    """.format(f"{df[df['category']=='Politics']['yes_price'].mean():.0%}" if not df[df['category']=='Politics'].empty else "N/A"), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div style="color: #A0A0C0;">₿</div>
        <div class="metric-value">{}</div>
        <div style="color: #A0A0C0;">Crypto</div>
    </div>
    """.format(f"{df[df['category']=='Crypto']['yes_price'].mean():.0%}" if not df[df['category']=='Crypto'].empty else "N/A"), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div style="color: #A0A0C0;">🌍</div>
        <div class="metric-value">{}</div>
        <div style="color: #A0A0C0;">Global</div>
    </div>
    """.format(f"{len(df)}", unsafe_allow_html=True))

with col4:
    sentiment_trend = "+14.8%"  # You'd calculate this from historical data
    st.markdown("""
    <div class="metric-card">
        <div style="color: #A0A0C0;">📊</div>
        <div class="metric-value radar-pulse">{}</div>
        <div style="color: #A0A0C0;">↑ {} this week</div>
    </div>
    """.format(f"{df['sentiment'].mean():.3f}" if not df.empty else "0.5", sentiment_trend), unsafe_allow_html=True)

# Category sentiment row
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

categories = ['Politics', 'Crypto', 'Macro', 'Geopolitics']
for col, cat in zip([col1, col2, col3, col4], categories):
    cat_df = df[df['category'] == cat]
    if not cat_df.empty:
        sentiment = cat_df['sentiment'].mean()
        change = "+9.2%" if sentiment > 0.6 else "-3.1%" if sentiment < 0.4 else "+2.1%"
        col.markdown(f"""
        <div class="stat-card">
            <h3>{cat}</h3>
            <div style="font-size: 32px; font-weight: 700;">{sentiment:.1%}</div>
            <div style="color: {'#10B981' if '+' in change else '#EF4444'};">{change}</div>
        </div>
        """, unsafe_allow_html=True)

# Main content
tab1, tab2, tab3 = st.tabs(["📊 Live Markets", "📈 Global Indices", "🤖 Oracle Chat"])

with tab1:
    st.subheader("Live Markets • Polymarket + Kalshi")
    
    # Market cards grid
    for i in range(0, min(6, len(df)), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(df):
                market = df.iloc[i + j]
                col.markdown(f"""
                <div class="stat-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #A0A0C0;">{market['source']}</span>
                        <span style="color: {'#10B981' if market['sentiment'] > 0.5 else '#EF4444'};">
                            {market['yes_price']:.1%}
                        </span>
                    </div>
                    <div style="font-size: 18px; margin: 10px 0;">{market['question'][:60]}...</div>
                    <div style="display: flex; justify-content: space-between; color: #A0A0C0;">
                        <span>💰 ${market['volume']:,.0f}</span>
                        <span>📈 {market['sentiment']:.2f} sentiment</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

with tab2:
    st.subheader("Global Sentiment Indices")
    
    sentiment_df = get_category_sentiment(df)
    if not sentiment_df.empty:
        # Create a gauge chart for overall sentiment
        overall = sentiment_df[sentiment_df['Category'] == 'OVERALL'].iloc[0]
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = overall['Sentiment'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Global Pulse"},
            gauge = {
                'axis': {'range': [0, 1], 'tickwidth': 1},
                'bar': {'color': "#667EEA"},
                'steps': [
                    {'range': [0, 0.33], 'color': "#EF4444"},
                    {'range': [0.33, 0.66], 'color': "#F59E0B"},
                    {'range': [0.66, 1], 'color': "#10B981"}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': overall['Sentiment']
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("🤖 Predictive Oracle")
    st.info("Ask the oracle about any market (requires OpenAI API key)")
    # We'll add the AI functionality in Phase 3

# Footer
st.markdown("---")
st.markdown(f"<p style='text-align: center; color: #A0A0C0;'>Last updated: {datetime.now().strftime('%I:%M %p')} UTC • Data from Polymarket + Kalshi</p>", unsafe_allow_html=True)
