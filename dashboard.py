import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Import our modules
from fetcher import get_all_markets
from sentiment import calculate_sentiment, get_category_sentiment

# Page config
st.set_page_config(
    page_title="PulseRadar • AI Predictive Sentiment Radar",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for the exact PulseRadar.xyz look
st.markdown("""
<style>
    /* Main background and text */
    .stApp {
        background: linear-gradient(180deg, #0A0A0F 0%, #1A1A2A 100%);
        color: #FFFFFF;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Custom typography */
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 64px;
        background: linear-gradient(135deg, #FFFFFF 0%, #A0A0C0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .subtitle {
        color: #A0A0C0;
        font-size: 18px;
        line-height: 1.6;
        text-align: center;
        max-width: 800px;
        margin: 20px auto;
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 24px;
        backdrop-filter: blur(10px);
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .metric-icon {
        font-size: 32px;
        margin-bottom: 16px;
        opacity: 0.9;
    }
    
    .metric-value {
        font-size: 48px;
        font-weight: 700;
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    
    .metric-label {
        color: #A0A0C0;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 8px;
    }
    
    /* Stat cards for categories */
    .stat-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px;
        transition: all 0.2s;
    }
    
    .stat-card:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .stat-category {
        font-size: 18px;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 12px;
    }
    
    .stat-value {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, #FFFFFF 0%, #C0C0E0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-change {
        font-size: 14px;
        margin-top: 8px;
    }
    
    .positive {
        color: #10B981;
    }
    
    .negative {
        color: #EF4444;
    }
    
    .neutral {
        color: #F59E0B;
    }
    
    /* Market cards */
    .market-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.2s;
    }
    
    .market-card:hover {
        background: rgba(255, 255, 255, 0.03);
        border-color: rgba(102, 126, 234, 0.4);
    }
    
    .market-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    
    .market-source {
        color: #667EEA;
        font-size: 13px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .market-probability {
        font-size: 20px;
        font-weight: 700;
    }
    
    .prob-high {
        color: #10B981;
    }
    
    .prob-low {
        color: #EF4444;
    }
    
    .prob-mid {
        color: #F59E0B;
    }
    
    .market-question {
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 12px;
        color: #FFFFFF;
    }
    
    .market-footer {
        display: flex;
        justify-content: space-between;
        color: #A0A0C0;
        font-size: 14px;
    }
    
    /* Radar pulse animation */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .radar-pulse {
        animation: pulse 2s infinite;
        display: inline-block;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.02);
        padding: 8px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 8px 16px;
        color: #A0A0C0;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(102, 126, 234, 0.2) !important;
        color: #FFFFFF !important;
    }
    
    /* Divider */
    .custom-divider {
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
        height: 1px;
        margin: 40px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header section with radar animation
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 style='text-align: center;'>📡</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>the radar<br>of the world</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class="subtitle">
        AI agents scour X, Facebook, TikTok, Instagram, global news headlines, blogs, 
        forums & public web sources in real time — then predict how Polymarket & Kalshi 
        markets will move based on real-world reaction patterns.
    </div>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_markets():
    with st.spinner("Scanning global markets..."):
        raw_df = get_all_markets(100)
        if not raw_df.empty:
            df = calculate_sentiment(raw_df)
            return df
        else:
            # Enhanced sample data for demo
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
                'source': ['Polymarket', 'Polymarket', 'Kalshi', 'Polymarket', 'Kalshi', 'Polymarket']
            })
            return calculate_sentiment(sample)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = load_markets()

df = st.session_state.df

# Top metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    politics_sentiment = df[df['category'] == 'Politics']['sentiment'].mean() if not df[df['category'] == 'Politics'].empty else 0.5
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🇺🇸</div>
        <div class="metric-value">{politics_sentiment:.0%}</div>
        <div class="metric-label">Politics</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    crypto_sentiment = df[df['category'] == 'Crypto']['sentiment'].mean() if not df[df['category'] == 'Crypto'].empty else 0.5
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">₿</div>
        <div class="metric-value">{crypto_sentiment:.0%}</div>
        <div class="metric-label">Crypto</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🌍</div>
        <div class="metric-value">{len(df)}</div>
        <div class="metric-label">markets tracked</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    global_sentiment = df['sentiment'].mean()
    # Calculate mock trend (in real app, compare with historical data)
    trend = "+14.8%" if global_sentiment > 0.6 else "-3.2%" if global_sentiment < 0.4 else "+5.1%"
    trend_class = "positive" if "+" in trend else "negative"
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-value radar-pulse">{global_sentiment:.3f}</div>
        <div class="metric-label">Global Sentiment <span class="{trend_class}">↑ {trend}</span></div>
    </div>
    """, unsafe_allow_html=True)

# Category stats row
st.markdown('<div style="margin: 40px 0;"></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
categories = ['Politics', 'Crypto', 'Macro', 'Geopolitics']
changes = ['+14.8%', '+9.2%', '-3.1%', '+27%']  # Mock changes

for col, cat, change in zip([col1, col2, col3, col4], categories, changes):
    cat_df = df[df['category'] == cat]
    if not cat_df.empty:
        sentiment = cat_df['sentiment'].mean()
        change_class = "positive" if "+" in change else "negative" if "-" in change else "neutral"
        
        col.markdown(f"""
        <div class="stat-card">
            <div class="stat-category">{cat}</div>
            <div class="stat-value">{sentiment:.0%}</div>
            <div class="stat-change {change_class}">{change}</div>
        </div>
        """, unsafe_allow_html=True)

# Custom divider
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Live Markets", "📈 Global Indices", "🤖 Oracle Chat"])

with tab1:
    st.markdown("### Live Markets • Polymarket + Kalshi")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.selectbox("Category", ["All", "Politics", "Crypto", "Macro", "Geopolitics", "Culture", "Technology"])
    with col2:
        platform_filter = st.selectbox("Platform", ["All", "Polymarket", "Kalshi"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Volume", "Sentiment", "Probability"])
    
    # Apply filters
    filtered_df = df.copy()
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    if platform_filter != "All":
        filtered_df = filtered_df[filtered_df['source'] == platform_filter]
    
    # Sort
    if sort_by == "Volume":
        filtered_df = filtered_df.sort_values('volume', ascending=False)
    elif sort_by == "Sentiment":
        filtered_df = filtered_df.sort_values('sentiment', ascending=False)
    else:
        filtered_df = filtered_df.sort_values('yes_price', ascending=False)
    
    # Display markets as cards
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
                <span>💰 Volume: ${market['volume']:,.0f}</span>
                <span>📊 Sentiment: {market['sentiment']:.3f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("### Global Sentiment Indices")
    
    sentiment_df = get_category_sentiment(df)
    
    if not sentiment_df.empty:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Gauge chart for overall sentiment
            overall = sentiment_df[sentiment_df['Category'] == 'OVERALL'].iloc[0]
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=overall['Sentiment'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Global Pulse Index", 'font': {'color': 'white', 'size': 20}},
                delta={'reference': 0.5, 'increasing': {'color': "#10B981"}, 'decreasing': {'color': "#EF4444"}},
                gauge={
                    'axis': {'range': [0, 1], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#667EEA"},
                    'bgcolor': 'rgba(0,0,0,0)',
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 0.33], 'color': 'rgba(239, 68, 68, 0.2)'},
                        {'range': [0.33, 0.66], 'color': 'rgba(245, 158, 11, 0.2)'},
                        {'range': [0.66, 1], 'color': 'rgba(16, 185, 129, 0.2)'}
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 4},
                        'thickness': 0.75,
                        'value': overall['Sentiment']
                    }
                }
            ))
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white', 'size': 12},
                height=350,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Bar chart of category sentiments
            cat_df = sentiment_df[sentiment_df['Category'] != 'OVERALL'].copy()
            
            fig2 = go.Figure(data=[
                go.Bar(
                    x=cat_df['Category'],
                    y=cat_df['Sentiment'],
                    marker_color=['#667EEA' for _ in range(len(cat_df))],
                    text=cat_df['Sentiment'].apply(lambda x: f'{x:.2%}'),
                    textposition='outside',
                    textfont={'color': 'white'}
                )
            ])
            
            fig2.update_layout(
                title={'text': "Sentiment by Category", 'font': {'color': 'white'}},
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis={'tickcolor': 'white', 'gridcolor': 'rgba(255,255,255,0.1)'},
                yaxis={'tickcolor': 'white', 'gridcolor': 'rgba(255,255,255,0.1)', 'range': [0, 1]},
                font={'color': 'white'},
                height=350,
                showlegend=False
            )
            
            fig2.add_hline(y=0.5, line_dash="dash", line_color="rgba(255,255,255,0.3)")
            
            st.plotly_chart(fig2, use_container_width=True)
        
        # Market stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Markets",
                overall['Markets'],
                delta=None
            )
        
        with col2:
            # Extract numeric value from Volume string (remove $ and ,)
            volume_str = overall['Volume'].replace('$', '').replace(',', '')
            st.metric(
                "Total Volume",
                f"${int(float(volume_str)):,}",
                delta=None
            )
        
        with col3:
            bullish_count = len(df[df['sentiment'] > 0.6])
            st.metric(
                "Bullish Markets",
                bullish_count,
                delta=f"{(bullish_count/len(df)*100):.0f}% of total"
            )
        
        with col4:
            bearish_count = len(df[df['sentiment'] < 0.4])
            st.metric(
                "Bearish Markets",
                bearish_count,
                delta=f"{(bearish_count/len(df)*100):.0f}% of total"
            )

with tab3:
    st.markdown("### 🤖 Predictive Oracle")
    
    # Check for API keys
    has_openai = os.getenv("OPENAI_API_KEY") is not None
    
    if not has_openai:
        st.info(
            "👋 **Ask the Oracle about any market**\n\n"
            "To enable AI predictions, add your OpenAI API key to secrets:\n"
            "```toml\n"
            'OPENAI_API_KEY = "sk-..."\n'
            "```\n\n"
            "The oracle can:\n"
            "- Predict market movements\n"
            "- Analyze sentiment trends\n"
            "- Answer questions about specific markets\n"
            "- Provide trading insights"
        )
    else:
        st.success("Oracle is ready! Ask me anything about the markets.")
        
        # Example queries as clickable buttons
        st.markdown("**Try asking:**")
        example_cols = st.columns(2)
        examples = [
            "Will Trump's probability increase after the debate?",
            "What's the sentiment on Bitcoin right now?",
            "Predict Fed rate cut odds for September",
            "Any markets showing unusual activity?"
        ]
        
        for i, ex in enumerate(examples):
            with example_cols[i % 2]:
                if st.button(f"💬 {ex}", key=f"example_{i}", use_container_width=True):
                    st.session_state['query'] = ex
        
        # Show the current query if any
        if 'query' in st.session_state:
            st.info(f"**Query:** {st.session_state['query']}")
            
            # Mock response (replace with actual AI call)
            with st.spinner("Analyzing markets and scanning signals..."):
                st.markdown("""
                **Oracle Response:**
                
                Based on current market data and sentiment analysis:
                
                - **Current probability**: 61%
                - **24h volume**: $2.4M
                - **Sentiment score**: 0.72 (Bullish)
                
                **Prediction**: +8-12% probability increase expected in next 6-12 hours based on:
                - Increasing social media chatter
                - Positive news sentiment
                - Whale accumulation detected
                
                Confidence: High (78%)
                """)
                
                # Clear button
                if st.button("Clear query", key="clear_query"):
                    del st.session_state['query']
                    st.rerun()
        
        # Add a text input at the bottom of the tab (not using chat_input)
        with st.form(key="oracle_form"):
            user_query = st.text_input("Ask the Oracle:", placeholder="e.g., What's the outlook for crypto markets?")
            submit_button = st.form_submit_button("Ask Oracle", use_container_width=True)
            
            if submit_button and user_query:
                st.session_state['query'] = user_query
                st.rerun()

# Footer
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col2:
    st.markdown(f"""
    <div style="text-align: center; color: #A0A0C0; padding: 20px;">
        <span class="radar-pulse">📡</span><br>
        <span>Last updated: {datetime.now().strftime('%I:%M %p')} UTC</span><br>
        <span style="font-size: 12px;">Data from Polymarket • Kalshi</span>
    </div>
    """, unsafe_allow_html=True)
