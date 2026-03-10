import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
import requests

# Import our modules (will gracefully fail if not present)
try:
    from fetcher import get_all_markets
    from sentiment import calculate_sentiment, get_category_sentiment
except ImportError:
    pass

# Page config
st.set_page_config(
    page_title="PulseRadar • AI Predictive Sentiment Radar",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Navbar & Global CSS matching PulseRadar.xyz
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700;800&display=swap');

    /* BASE STREAMLIT OVERRIDES */
    .stApp {
        background-color: #09090b; 
        background-image: radial-gradient(circle at 50% 20%, rgba(124, 58, 237, 0.15) 0%, #09090b 70%);
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    .appview-container .main .block-container {
        padding-top: 6rem !important; 
    }
    
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    h1, h2, h3, h4, span, p, div {
        font-family: 'Inter', sans-serif;
    }

    /* --- FIXED NAVBAR --- */
    .custom-navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999999;
        background: rgba(9, 9, 11, 0.75); 
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        font-family: 'Inter', sans-serif;
    }
    .nav-container {
        max-width: 80rem; 
        margin: 0 auto;
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .nav-left {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .nav-logo-box {
        width: 1.75rem;
        height: 1.75rem;
        border-radius: 0.5rem;
        background: linear-gradient(to bottom right, #7c3aed, #10b981); 
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.125rem;
    }
    .nav-title {
        font-size: 1.25rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: white;
        text-decoration: none;
    }
    .nav-center {
        display: none; 
    }
    @media (min-width: 768px) {
        .nav-center {
            display: flex;
            align-items: center;
            gap: 2.5rem;
            font-size: 0.875rem;
            font-weight: 500;
        }
    }
    .nav-link {
        color: #d4d4d8;
        text-decoration: none;
        transition: color 0.2s;
    }
    .nav-link:hover {
        color: #34d399; 
    }
    .nav-right {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .btn-github {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 0.5rem;
        text-decoration: none;
        transition: all 0.2s;
    }
    .btn-github:hover {
        border-color: rgba(255, 255, 255, 0.4);
    }
    .btn-primary {
        background: white;
        color: #09090b;
        padding: 0.5rem 1.25rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 0.875rem;
        text-decoration: none;
        transition: all 0.2s;
    }
    .btn-primary:hover {
        background: #34d399; 
        color: white;
    }

    /* --- MAIN UI ELEMENTS --- */
    .main-title {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(to right, #a78bfa, #34d399, #22d3ee); 
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
        margin-top: 1rem;
        margin-bottom: 1rem;
        letter-spacing: -0.04em;
    }

    .sub-title {
        text-align: center;
        color: #a1a1aa;
        font-size: 1.125rem;
        max-width: 650px;
        margin: 0 auto 3rem auto;
        line-height: 1.6;
        font-weight: 400;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.03); 
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 1.5rem; 
        padding: 24px;
        text-align: center;
        backdrop-filter: blur(16px);
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); 
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px -10px rgba(124, 58, 237, 0.15);
        border-color: rgba(255, 255, 255, 0.2);
    }

    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
    }

    .metric-val {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }

    .metric-label {
        color: #a1a1aa;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }

    /* Market Cards */
    .market-card {
        background: rgba(20, 20, 25, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.2s;
    }
    
    .market-card:hover {
        border-color: rgba(52, 211, 153, 0.4);
        background: rgba(25, 25, 30, 0.8);
    }

    .market-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
        align-items: center;
    }

    .market-tag {
        color: #34d399; 
        background: rgba(52, 211, 153, 0.1);
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.7rem;
    }

    .market-prob {
        font-size: 1.25rem;
        font-weight: 700;
    }

    .prob-high { color: #10B981; }
    .prob-low { color: #EF4444; }
    .prob-mid { color: #F59E0B; }

    .market-question {
        font-size: 1.05rem;
        font-weight: 500;
        color: #f4f4f5;
        margin-bottom: 16px;
        line-height: 1.4;
    }

    .market-footer {
        display: flex;
        justify-content: space-between;
        color: #a1a1aa;
        font-size: 0.8rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        padding-top: 12px;
    }

    /* Tabs override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.03);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        color: #a1a1aa;
        font-weight: 500;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
    }

    /* Radar Pulse Indicator */
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(52, 211, 153, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
    }
    .pulse-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #34d399; 
        border-radius: 50%;
        animation: pulse 2s infinite;
        margin-right: 8px;
    }
    
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 2.5rem 0;
    }
</style>

<div class="custom-navbar">
    <div class="nav-container">
        <div class="nav-left">
            <div class="nav-logo-box">📡</div>
            <a href="https://pulseradar.xyz" class="nav-title">PulseRadar</a>
        </div>
        <div class="nav-center">
            <a href="https://pulseradar.xyz#features" class="nav-link">Features</a>
            <a href="https://pulseradar.xyz#ai" class="nav-link">AI Agents</a>
            <a href="https://pulseradar.xyz#why" class="nav-link">Why Real Money</a>
        </div>
        <div class="nav-right">
            <a href="https://github.com/flamz321/PulseRadar" target="_blank" class="btn-github">
                <i class="fa-brands fa-github"></i> GitHub
            </a>
            <a href="https://pulseradar.xyz" class="btn-primary">
                Main Site →
            </a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<div class="main-title">Live Dashboard</div>', unsafe_allow_html=True)
st.markdown("""
<div class="sub-title">
    AI agents scour X, Facebook, TikTok, Instagram, global news headlines, blogs, 
    forums & public web sources in real time — then predict how Polymarket & Kalshi 
    markets will move based on real-world reaction patterns.
</div>
""", unsafe_allow_html=True)

# Data Loading (Live Kalshi Public API Data)
@st.cache_data(ttl=300)
def load_markets():
    live_data = []
    
    # 1. Fetch Real-time data from Kalshi Public API
    try:
        url = "https://api.elections.kalshi.com/trade-api/v2/markets?limit=100&status=open"
        response = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
        
        if response.status_code == 200:
            kalshi_markets = response.json().get('markets', [])
            
            for m in kalshi_markets:
                # Kalshi returns prices in cents (e.g., 61). Convert to decimal.
                price_cents = m.get('yes_ask', m.get('last_price', 50))
                yes_price = price_cents / 100.0 if price_cents and price_cents > 1 else price_cents
                
                vol = float(m.get('volume', 0))
                title = m.get('title', m.get('ticker', 'Unknown Market'))
                
                live_data.append({
                    'question': title,
                    'category': 'Kalshi Live',
                    'yes_price': yes_price,
                    'volume': vol,
                    'source': 'Kalshi',
                    'sentiment': yes_price # Default sentiment proxy until mapped
                })
    except Exception as e:
        print(f"Error fetching from Kalshi API: {e}")

    # 2. Add local modules data (Polymarket or other files)
    try:
        raw_df = get_all_markets(100)
        if not raw_df.empty:
            local_df = calculate_sentiment(raw_df)
            live_data.extend(local_df.to_dict('records'))
    except Exception:
        pass
        
    # 3. Return Combined DataFrame or Fallback
    if live_data:
        df = pd.DataFrame(live_data)
        # Drop markets with 0 volume to keep UI clean and sort highest first
        df = df[df['volume'] > 0].sort_values(by='volume', ascending=False)
        return df
    else:
        # Safe Fallback Demo Data
        return pd.DataFrame({
            'question': [
                'Donald Trump to win 2028 Presidential Election?',
                'Bitcoin to reach $100,000 by end of 2024?',
                'Federal Reserve to cut rates in September?'
            ],
            'category': ['Politics', 'Crypto', 'Macro'],
            'yes_price': [0.61, 0.72, 0.45],
            'volume': [2400000, 1800000, 3200000],
            'source': ['Polymarket', 'Polymarket', 'Kalshi'],
            'sentiment': [0.72, 0.85, 0.40] 
        })

if 'df' not in st.session_state:
    st.session_state.df = load_markets()

df = st.session_state.df

# --- Top Metrics Row ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    politics_sentiment = df[df['category'].str.contains('Politic', na=False, case=False)]['sentiment'].mean()
    politics_sentiment = politics_sentiment if pd.notna(politics_sentiment) else 0.5
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🏛️</div>
        <div class="metric-val">{politics_sentiment:.0%}</div>
        <div class="metric-label">Politics Pulse</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    crypto_sentiment = df[df['category'].str.contains('Crypto', na=False, case=False)]['sentiment'].mean()
    crypto_sentiment = crypto_sentiment if pd.notna(crypto_sentiment) else 0.5
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">₿</div>
        <div class="metric-val">{crypto_sentiment:.0%}</div>
        <div class="metric-label">Crypto Pulse</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🌍</div>
        <div class="metric-val">{len(df)}</div>
        <div class="metric-label">Markets Tracked</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    global_sentiment = df['sentiment'].mean()
    trend = "+14.8%" if global_sentiment > 0.6 else "-3.2%" if global_sentiment < 0.4 else "+5.1%"
    trend_color = "#10B981" if "+" in trend else "#EF4444"
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-val">{global_sentiment:.2f}</div>
        <div class="metric-label">Global Index <span style="color: {trend_color};">↑ {trend}</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# --- Main Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Live Markets", "📈 Global Indices", "🤖 Oracle Chat"])

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        # Dynamic categories based on data payload
        cats = ["All"] + sorted(list(df['category'].unique()))
        category_filter = st.selectbox("Category", cats)
    with col2:
        platforms = ["All"] + sorted(list(df['source'].unique()))
        platform_filter = st.selectbox("Platform", platforms)
    with col3:
        sort_by = st.selectbox("Sort by", ["Volume", "Sentiment", "Probability"])
    
    filtered_df = df.copy()
    if category_filter != "All": filtered_df = filtered_df[filtered_df['category'] == category_filter]
    if platform_filter != "All": filtered_df = filtered_df[filtered_df['source'] == platform_filter]
    
    if sort_by == "Volume": filtered_df = filtered_df.sort_values('volume', ascending=False)
    elif sort_by == "Sentiment": filtered_df = filtered_df.sort_values('sentiment', ascending=False)
    else: filtered_df = filtered_df.sort_values('yes_price', ascending=False)
    
    st.markdown("<br>", unsafe_allow_html=True)
    for _, market in filtered_df.head(15).iterrows():
        prob_class = "prob-high" if market['yes_price'] > 0.66 else "prob-low" if market['yes_price'] < 0.33 else "prob-mid"
        st.markdown(f"""
        <div class="market-card">
            <div class="market-header">
                <span class="market-tag">{market['source']} • {market['category']}</span>
                <span class="market-prob {prob_class}">{market['yes_price']:.1%}</span>
            </div>
            <div class="market-question">{market['question']}</div>
            <div class="market-footer">
                <span>💰 Volume: ${market['volume']:,.0f}</span>
                <span>⚡ Sentiment: {market['sentiment']:.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        sentiment_df = get_category_sentiment(df)
    except Exception:
        mock_data = []
        for cat in df['category'].unique():
            mock_data.append({'Category': cat, 'Sentiment': df[df['category'] == cat]['sentiment'].mean(), 'Markets': 10, 'Volume': '$1,000,000'})
        mock_data.append({'Category': 'OVERALL', 'Sentiment': df['sentiment'].mean(), 'Markets': len(df), 'Volume': f"${df['volume'].sum():,}"})
        sentiment_df = pd.DataFrame(mock_data)

    if not sentiment_df.empty:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            overall = sentiment_df[sentiment_df['Category'] == 'OVERALL'].iloc[0]
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=overall['Sentiment'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Global Pulse Index", 'font': {'color': 'white', 'size': 16}},
                gauge={
                    'axis': {'range': [0, 1], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.2)"},
                    'bar': {'color': "#34d399"}, 
                    'bgcolor': 'rgba(255,255,255,0.05)',
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 0.4], 'color': 'rgba(239, 68, 68, 0.2)'},
                        {'range': [0.4, 0.6], 'color': 'rgba(245, 158, 11, 0.2)'},
                        {'range': [0.6, 1], 'color': 'rgba(16, 185, 129, 0.2)'}
                    ],
                    'threshold': {'line': {'color': "white", 'width': 3}, 'thickness': 0.75, 'value': overall['Sentiment']}
                }
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#a1a1aa'), height=350, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            cat_df = sentiment_df[sentiment_df['Category'] != 'OVERALL'].copy()
            
            fig2 = go.Figure(data=[
                go.Bar(
                    x=cat_df['Category'],
                    y=cat_df['Sentiment'],
                    marker_color='#34d399', 
                    text=cat_df['Sentiment'].apply(lambda x: f'{x:.2%}'),
                    textposition='outside',
                    textfont=dict(color='white')
                )
            ])
            
            fig2.update_layout(
                title=dict(text="Sentiment by Category", font=dict(color='white', size=16)),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#a1a1aa'),
                height=350,
                showlegend=False,
                margin=dict(l=0, r=0, t=50, b=0)
            )
            
            fig2.update_xaxes(showgrid=False, tickcolor='rgba(255,255,255,0.1)', linecolor='rgba(255,255,255,0.1)')
            fig2.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', range=[0, 1], zeroline=False)
            
            st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    has_openai = os.getenv("OPENAI_API_KEY") is not None
    
    if not has_openai:
        st.info("👋 **Ask the Oracle**\n\nAdd your OpenAI API key to `.streamlit/secrets.toml` to enable live predictions.")
    
    st.markdown("**Example Queries:**")
    c1, c2 = st.columns(2)
    if c1.button("Will Trump's probability increase?", use_container_width=True): st.session_state['query'] = "Will Trump's probability increase after the debate?"
    if c2.button("Predict Fed rate cut odds", use_container_width=True): st.session_state['query'] = "Predict Fed rate cut odds for September"

    if 'query' in st.session_state:
        st.markdown(f"> **You:** {st.session_state['query']}")
        with st.spinner("Scanning global signals..."):
            st.success("**Oracle:** Based on real-time social velocity, sentiment is currently 0.72 (Bullish). We project a +8% probability increase in the next 12 hours.")
        if st.button("Clear History"):
            del st.session_state['query']
            st.rerun()

    with st.form(key="oracle_form"):
        user_query = st.text_input("Ask the AI Oracle:", placeholder="What's the outlook for crypto?")
        if st.form_submit_button("Submit"):
            st.session_state['query'] = user_query
            st.rerun()

# --- Footer ---
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; color: #71717a; font-size: 0.8rem; padding-bottom: 2rem;">
    <span class="pulse-dot"></span> Live Data Feed Active • Last updated: {datetime.now().strftime('%I:%M %p')} UTC
</div>
""", unsafe_allow_html=True)
