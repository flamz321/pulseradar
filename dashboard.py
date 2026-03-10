import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Import our modules (mocked for this example)
from fetcher import get_all_markets
from sentiment import calculate_sentiment, get_category_sentiment

# Page config
st.set_page_config(
    page_title="PulseRadar • AI Predictive Sentiment",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a sleek, modern Web3 aesthetic
st.markdown("""
<style>
    /* Main background and text */
    .stApp {
        background: linear-gradient(180deg, #09090E 0%, #12121A 100%);
        color: #F8F9FA;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu, header, footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Custom typography */
    h1, h2, h3 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 800;
        letter-spacing: -0.03em;
    }
    
    h1 {
        font-size: 56px;
        background: linear-gradient(135deg, #FFFFFF 0%, #8E8EA0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        line-height: 1.1;
    }
    
    .subtitle {
        color: #8E8EA0;
        font-size: 16px;
        line-height: 1.5;
        text-align: center;
        max-width: 700px;
        margin: 16px auto 32px auto;
        font-weight: 400;
    }
    
    /* Modern Glassmorphism Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(12px);
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(102, 126, 234, 0.4);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
    }
    
    .metric-icon {
        font-size: 28px;
        margin-bottom: 12px;
    }
    
    .metric-value {
        font-size: 40px;
        font-weight: 800;
        background: linear-gradient(135deg, #667EEA 0%, #9F7AEA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    
    .metric-label {
        color: #8E8EA0;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 8px;
        font-weight: 600;
    }
    
    /* Stat cards for categories */
    .stat-card {
        background: rgba(255, 255, 255, 0.015);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 12px;
        padding: 16px;
        transition: all 0.2s;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .stat-card:hover {
        background: rgba(255, 255, 255, 0.03);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .stat-category {
        font-size: 14px;
        font-weight: 500;
        color: #A0A0C0;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: #FFFFFF;
    }
    
    .stat-change {
        font-size: 13px;
        margin-top: 4px;
        font-weight: 500;
    }
    
    .positive { color: #10B981; }
    .negative { color: #EF4444; }
    .neutral { color: #F59E0B; }
    
    /* Market cards */
    .market-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
        transition: all 0.2s;
    }
    
    .market-card:hover {
        background: rgba(255, 255, 255, 0.03);
        border-color: rgba(102, 126, 234, 0.4);
    }
    
    .market-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .market-source {
        background: rgba(102, 126, 234, 0.1);
        color: #8C9EFF;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .market-probability {
        font-size: 22px;
        font-weight: 800;
    }
    
    .prob-high { color: #10B981; }
    .prob-low { color: #EF4444; }
    .prob-mid { color: #F59E0B; }
    
    .market-question {
        font-size: 17px;
        font-weight: 500;
        margin-bottom: 16px;
        color: #FFFFFF;
        line-height: 1.4;
    }
    
    .market-footer {
        display: flex;
        justify-content: space-between;
        color: #8E8EA0;
        font-size: 13px;
        border-top: 1px solid rgba(255,255,255,0.05);
        padding-top: 12px;
    }
    
    /* Radar pulse animation */
    @keyframes pulse {
        0% { opacity: 0.5; text-shadow: 0 0 0px rgba(102,126,234,0); }
        50% { opacity: 1; text-shadow: 0 0 15px rgba(102,126,234,0.6); }
        100% { opacity: 0.5; text-shadow: 0 0 0px rgba(102,126,234,0); }
    }
    
    .radar-pulse {
        animation: pulse 2.5s infinite;
        display: inline-block;
    }
    
    /* Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(0, 0, 0, 0.2);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        color: #8E8EA0;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(102, 126, 234, 0.15) !important;
        color: #FFFFFF !important;
        border-bottom: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Header section
st.markdown("<h1 style='text-align: center;'><span class='radar-pulse'>📡</span> PulseRadar</h1>", unsafe_allow_html=True)
st.markdown("""
<div class="subtitle">
    AI agents scour X, Facebook, TikTok, global news, blogs, and forums in real time — 
    predicting Polymarket & Kalshi movements based on real-world reaction patterns.
</div>
""", unsafe_allow_html=True)

# --- Mock Data Loader ---
@st.cache_data(ttl=300)
def load_markets():
    try:
        raw_df = get_all_markets(100)
        if not raw_df.empty:
            return calculate_sentiment(raw_df)
    except:
        pass
        
    # Fallback/Demo data
    sample = pd.DataFrame({
        'question': [
            'Donald Trump to win 2028 Presidential Election?',
            'Bitcoin to reach $100,000 by end of 2024?',
            'Federal Reserve to cut rates in September?',
            'EU to approve new migration pact this year?',
            'SpaceX to complete Starship orbital test?',
            'Taylor Swift to endorse Biden in 2024?'
        ],
        'category': ['Politics', 'Crypto', 'Macro', 'Geopolitics', 'Technology', 'Culture'],
        'yes_price': [0.61, 0.72, 0.45, 0.83, 0.34, 0.67],
        'volume': [2400000, 1800000, 3200000, 950000, 1500000, 2100000],
        'source': ['Polymarket', 'Polymarket', 'Kalshi', 'Polymarket', 'Kalshi', 'Polymarket'],
        'sentiment': [0.72, 0.85, 0.40, 0.65, 0.80, 0.55] 
    })
    return sample

if 'df' not in st.session_state:
    st.session_state.df = load_markets()

df = st.session_state.df

# --- Top Metrics Row ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    politics_sentiment = df[df['category'] == 'Politics']['sentiment'].mean() if not df[df['category'] == 'Politics'].empty else 0.5
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🏛️</div>
        <div class="metric-value">{politics_sentiment:.0%}</div>
        <div class="metric-label">Politics Pulse</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    crypto_sentiment = df[df['category'] == 'Crypto']['sentiment'].mean() if not df[df['category'] == 'Crypto'].empty else 0.5
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">₿</div>
        <div class="metric-value">{crypto_sentiment:.0%}</div>
        <div class="metric-label">Crypto Pulse</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🌐</div>
        <div class="metric-value">{len(df)}</div>
        <div class="metric-label">Markets Tracked</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    global_sentiment = df['sentiment'].mean()
    trend = "+14.8%" if global_sentiment > 0.6 else "-3.2%" if global_sentiment < 0.4 else "+5.1%"
    trend_class = "positive" if "+" in trend else "negative"
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📈</div>
        <div class="metric-value radar-pulse">{global_sentiment:.2f}</div>
        <div class="metric-label">Global Index <span class="{trend_class}">↑ {trend}</span></div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- Main Interface Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Live Markets", "📈 Global Indices", "🤖 Oracle Chat"])

# TAB 1: Live Markets
with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.selectbox("Category Filter", ["All", "Politics", "Crypto", "Macro", "Geopolitics", "Culture", "Technology"])
    with col2:
        platform_filter = st.selectbox("Platform Filter", ["All", "Polymarket", "Kalshi"])
    with col3:
        sort_by = st.selectbox("Sort Data By", ["Volume", "Sentiment", "Probability"])
    
    filtered_df = df.copy()
    if category_filter != "All": filtered_df = filtered_df[filtered_df['category'] == category_filter]
    if platform_filter != "All": filtered_df = filtered_df[filtered_df['source'] == platform_filter]
    
    if sort_by == "Volume": filtered_df = filtered_df.sort_values('volume', ascending=False)
    elif sort_by == "Sentiment": filtered_df = filtered_df.sort_values('sentiment', ascending=False)
    else: filtered_df = filtered_df.sort_values('yes_price', ascending=False)
    
    st.markdown("<br>", unsafe_allow_html=True)
    for _, market in filtered_df.head(10).iterrows():
        prob_class = "prob-high" if market['yes_price'] > 0.66 else "prob-low" if market['yes_price'] < 0.33 else "prob-mid"
        st.markdown(f"""
        <div class="market-card">
            <div class="market-header">
                <span class="market-source">{market['source']} • {market['category']}</span>
                <span class="market-probability {prob_class}">{market['yes_price']:.1%}</span>
            </div>
            <div class="market-question">{market['question']}</div>
            <div class="market-footer">
                <span>💰 Vol: ${market['volume']:,.0f}</span>
                <span>⚡ Sentiment: {market['sentiment']:.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# TAB 2: Global Indices
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Gauge Chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=global_sentiment,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Global Pulse Index", 'font': {'color': '#8E8EA0', 'size': 16}},
            gauge={
                'axis': {'range': [0, 1], 'tickwidth': 1, 'tickcolor': "#4A4A5A"},
                'bar': {'color': "#8C9EFF"},
                'bgcolor': 'rgba(255,255,255,0.02)',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 0.4], 'color': 'rgba(239, 68, 68, 0.15)'},
                    {'range': [0.4, 0.6], 'color': 'rgba(245, 158, 11, 0.15)'},
                    {'range': [0.6, 1], 'color': 'rgba(16, 185, 129, 0.15)'}
                ],
                'threshold': {'line': {'color': "#FFFFFF", 'width': 3}, 'thickness': 0.75, 'value': global_sentiment}
            }
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': 'white'}, height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Mini Category breakdown
        cat_group = df.groupby('category')['sentiment'].mean().reset_index()
        fig2 = px.bar(cat_group, x='category', y='sentiment', text_auto='.2f', color_discrete_sequence=['#8C9EFF'])
        
        # FIX: Flat layout update to avoid dictionary validation clashes
        fig2.update_layout(
            title_text="Sentiment by Category",
            title_font=dict(color='#8E8EA0', size=16),
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white', 
            height=300, 
            showlegend=False, 
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        # FIX: Update axes independently
        fig2.update_xaxes(showgrid=False, tickcolor='#4A4A5A')
        fig2.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', range=[0, 1])
        
        st.plotly_chart(fig2, use_container_width=True)

# TAB 3: Oracle Chat (Refactored to native st.chat)
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello. I am the Pulse Oracle. I scan global sentiment across social networks to predict Polymarket and Kalshi outcomes. What market would you like to analyze?"}
        ]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Suggested prompts
    if len(st.session_state.messages) == 1:
        st.caption("Suggested Queries:")
        c1, c2, c3 = st.columns(3)
        if c1.button("Trump Debate Odds?", use_container_width=True): st.session_state.preset = "Will Trump's probability increase after the debate?"
        if c2.button("BTC Sentiment?", use_container_width=True): st.session_state.preset = "What's the sentiment on Bitcoin right now?"
        if c3.button("Fed Rate Cut?", use_container_width=True): st.session_state.preset = "Predict Fed rate cut odds for September"

    # Handle Chat Input
    user_input = st.chat_input("Ask the Oracle...")
    query = st.session_state.pop("preset", None) or user_input

    if query:
        # Append User Message
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
            
        # Append Mock Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("Scanning signals..."):
                response = f"**Analysis for:** '{query}'\n\nBased on social velocity, sentiment is currently **0.72 (Bullish)**. We project a +8% probability increase in the next 12 hours due to rising chatter volume."
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# --- Footer ---
st.markdown("""
<div style="text-align: center; color: #4A4A5A; margin-top: 50px; font-size: 13px;">
    <span class="radar-pulse">📡</span> Live Data Feed Active<br>
    Polymarket • Kalshi
</div>
""", unsafe_allow_html=True)
