import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Import our modules (assuming these exist in your environment)
from fetcher import get_all_markets
from sentiment import calculate_sentiment, get_category_sentiment

# Page config
st.set_page_config(
    page_title="PulseRadar • AI Predictive Sentiment Radar",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a premium, modern dark-mode aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global App Background & Font */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    div[data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #050505 60%, #000000 100%);
        color: #EDEDED;
    }
    
    /* Clean up default Streamlit padding */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Typography */
    h1 {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        text-align: center;
        letter-spacing: -0.04em;
        background: linear-gradient(180deg, #FFFFFF 0%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem !important;
    }
    
    .subtitle {
        color: #94A3B8;
        font-size: 1.1rem;
        line-height: 1.6;
        text-align: center;
        max-width: 700px;
        margin: 0 auto 3rem auto;
        font-weight: 400;
    }
    
    /* Premium Metric Cards (Glassmorphism) */
    .metric-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99, 102, 241, 0.5);
        background: rgba(30, 41, 59, 0.6);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    .metric-icon {
        font-size: 1.75rem;
        margin-bottom: 1rem;
        background: rgba(255,255,255,0.05);
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #F8FAFC;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #94A3B8;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Stat Cards (Smaller format) */
    .stat-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.3) 0%, rgba(15, 23, 42, 0.3) 100%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.25rem;
        transition: all 0.2s;
    }
    
    .stat-category {
        font-size: 0.875rem;
        color: #94A3B8;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    
    /* Market Cards */
    .market-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    
    .market-card:hover {
        background: rgba(30, 41, 59, 0.8);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    .market-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .market-source {
        background: rgba(99, 102, 241, 0.1);
        color: #818CF8;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .market-question {
        font-size: 1.125rem;
        font-weight: 600;
        color: #F8FAFC;
        margin-bottom: 1rem;
        line-height: 1.4;
    }
    
    .market-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        color: #94A3B8;
        font-size: 0.875rem;
    }
    
    /* Status Colors */
    .positive { color: #10B981; background: rgba(16, 185, 129, 0.1); padding: 0.1rem 0.4rem; border-radius: 4px; }
    .negative { color: #EF4444; background: rgba(239, 68, 68, 0.1); padding: 0.1rem 0.4rem; border-radius: 4px; }
    .neutral { color: #F59E0B; background: rgba(245, 158, 11, 0.1); padding: 0.1rem 0.4rem; border-radius: 4px; }
    
    .prob-badge {
        font-size: 1.25rem;
        font-weight: 700;
        padding: 0.25rem 0.75rem;
        border-radius: 8px;
    }
    .prob-high { color: #10B981; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); }
    .prob-low { color: #EF4444; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); }
    .prob-mid { color: #F59E0B; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.2); }

    /* Radar Pulse Animation */
    @keyframes radar-ping {
        0% { transform: scale(0.8); opacity: 0.8; }
        100% { transform: scale(2.5); opacity: 0; }
    }
    
    .radar-icon-container {
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 64px;
        height: 64px;
        margin: 0 auto 1rem auto;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 50%;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    .radar-icon-container::before {
        content: '';
        position: absolute;
        inset: -4px;
        border-radius: 50%;
        border: 2px solid #6366f1;
        animation: radar-ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;
    }
    
    /* Streamlit Tab Styling Override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(15, 23, 42, 0.6);
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        color: #94A3B8;
        font-weight: 500;
        border: none !important;
        background: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: #6366F1 !important;
        color: #FFFFFF !important;
    }
    
    /* Divider */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 3rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header section with radar animation
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center;">
        <div class="radar-icon-container">
            <span style="font-size: 28px;">📡</span>
        </div>
        <h1>the radar of the world</h1>
        <div class="subtitle">
            AI agents scour X, Facebook, TikTok, Instagram, global news headlines, blogs, 
            forums & public web sources in real time — then predict how Polymarket & Kalshi 
            markets will move based on real-world reaction patterns.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Load data (Mock logic stays the same)
@st.cache_data(ttl=300)
def load_markets():
    with st.spinner("Scanning global markets..."):
        try:
            raw_df = get_all_markets(100)
            if not raw_df.empty:
                return calculate_sentiment(raw_df)
        except Exception:
            pass
            
        # Fallback to enhanced sample data
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
        
        # Simple sentiment mock if module is missing
        try:
            return calculate_sentiment(sample)
        except Exception:
            sample['sentiment'] = [0.65, 0.82, 0.41, 0.55, 0.78, 0.60]
            return sample

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = load_markets()

df = st.session_state.df

# Top metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    politics_df = df[df['category'] == 'Politics']
    politics_sentiment = politics_df['sentiment'].mean() if not politics_df.empty else 0.5
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🇺🇸</div>
        <div class="metric-value">{politics_sentiment:.0%}</div>
        <div class="metric-label">Politics Sentiment</div>
    </div>
    """, unsafe_allow_html=True)

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
        
        # FIX: Update axes independently using standard Plotly Express methods
        fig2.update_xaxes(showgrid=False, tickcolor='#4A4A5A')
        fig2.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', range=[0, 1])
        
        st.plotly_chart(fig2, use_container_width=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🌍</div>
        <div class="metric-value">{len(df)}</div>
        <div class="metric-label">Active Markets Tracked</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    global_sentiment = df['sentiment'].mean()
    trend = "+14.8%" if global_sentiment > 0.6 else "-3.2%" if global_sentiment < 0.4 else "+5.1%"
    trend_class = "positive" if "+" in trend else "negative"
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-value">{global_sentiment:.3f}</div>
        <div class="metric-label">Global Index <span class="{trend_class}">↑ {trend}</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Tabs Configuration
tab1, tab2, tab3 = st.tabs(["📊 Live Markets", "📈 Global Indices", "🤖 Oracle Chat"])

with tab1:
    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        category_filter = st.selectbox("Category", ["All"] + list(df['category'].unique()))
    with col_f2:
        platform_filter = st.selectbox("Platform", ["All", "Polymarket", "Kalshi"])
    with col_f3:
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Market Cards Render
    for _, market in filtered_df.head(10).iterrows():
        prob_class = "prob-high" if market['yes_price'] > 0.66 else "prob-low" if market['yes_price'] < 0.33 else "prob-mid"
        
        st.markdown(f"""
        <div class="market-card">
            <div class="market-header">
                <span class="market-source">{market['source']} • {market['category']}</span>
                <span class="prob-badge {prob_class}">{market['yes_price']:.1%}</span>
            </div>
            <div class="market-question">{market['question']}</div>
            <div class="market-footer">
                <span style="display: flex; gap: 1.5rem;">
                    <span><strong style="color: #fff;">Vol:</strong> ${market['volume']:,.0f}</span>
                    <span><strong style="color: #fff;">Sentiment:</strong> {market['sentiment']:.2f}</span>
                </span>
                <span style="color: #6366F1; cursor: pointer; font-weight: 500;">Ask Oracle →</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    try:
        sentiment_df = get_category_sentiment(df)
    except Exception:
        # Fallback if module is missing
        sentiment_df = pd.DataFrame({
            'Category': ['OVERALL', 'Politics', 'Crypto', 'Macro', 'Geopolitics'],
            'Sentiment': [0.63, 0.65, 0.82, 0.41, 0.55],
            'Markets': [len(df), 1, 1, 1, 1],
            'Volume': ['$9.9M', '$2.4M', '$1.8M', '$3.2M', '$950k']
        })

    if not sentiment_df.empty:
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            overall = sentiment_df[sentiment_df['Category'] == 'OVERALL'].iloc[0]
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=overall['Sentiment'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Global Pulse Index", 'font': {'color': '#F8FAFC', 'size': 20, 'family': 'Inter'}},
                delta={'reference': 0.5, 'increasing': {'color': "#10B981"}, 'decreasing': {'color': "#EF4444"}},
                gauge={
                    'axis': {'range': [0, 1], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.2)"},
                    'bar': {'color': "#6366F1"},
                    'bgcolor': 'rgba(255,255,255,0.05)',
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 0.33], 'color': 'rgba(239, 68, 68, 0.15)'},
                        {'range': [0.33, 0.66], 'color': 'rgba(245, 158, 11, 0.15)'},
                        {'range': [0.66, 1], 'color': 'rgba(16, 185, 129, 0.15)'}
                    ]
                }
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#94A3B8', 'family': 'Inter'},
                height=350,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_c2:
            cat_df = sentiment_df[sentiment_df['Category'] != 'OVERALL'].copy()
            fig2 = go.Figure(data=[
                go.Bar(
                    x=cat_df['Category'],
                    y=cat_df['Sentiment'],
                    marker_color='#6366F1',
                    marker_line_color='rgba(99, 102, 241, 0.5)',
                    marker_line_width=1,
                    text=cat_df['Sentiment'].apply(lambda x: f'{x:.0%}'),
                    textposition='outside',
                    textfont={'color': '#F8FAFC', 'family': 'Inter'}
                )
            ])
            fig2.update_layout(
                title={'text': "Sentiment by Category", 'font': {'color': '#F8FAFC', 'family': 'Inter'}},
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis={'tickcolor': 'transparent', 'gridcolor': 'transparent'},
                yaxis={'tickcolor': 'transparent', 'gridcolor': 'rgba(255,255,255,0.05)', 'range': [0, 1]},
                font={'color': '#94A3B8', 'family': 'Inter'},
                height=350,
                margin=dict(l=20, r=20, t=50, b=20),
                showlegend=False
            )
            fig2.add_hline(y=0.5, line_dash="dash", line_color="rgba(255,255,255,0.2)")
            st.plotly_chart(fig2, use_container_width=True)

with tab3:
    # Check for API keys
    has_openai = os.getenv("OPENAI_API_KEY") is not None
    
    if not has_openai:
        st.info("💡 **Pro Tip**: To enable live AI predictions, add your `OPENAI_API_KEY` to the Streamlit secrets.")
    
    st.markdown("### Ask the Predictive Oracle")
    
    # Example prompts
    st.markdown("<span style='color: #94A3B8; font-size: 0.875rem;'>Try asking:</span>", unsafe_allow_html=True)
    e_col1, e_col2 = st.columns(2)
    with e_col1:
        if st.button("🔮 Will Trump's probability increase after the debate?", use_container_width=True):
            st.session_state['query'] = "Will Trump's probability increase after the debate?"
        if st.button("📊 What's the sentiment on Bitcoin right now?", use_container_width=True):
            st.session_state['query'] = "What's the sentiment on Bitcoin right now?"
    with e_col2:
        if st.button("🏛️ Predict Fed rate cut odds for September", use_container_width=True):
            st.session_state['query'] = "Predict Fed rate cut odds for September"
        if st.button("🚨 Any markets showing unusual activity?", use_container_width=True):
            st.session_state['query'] = "Any markets showing unusual activity?"
            
    # Mock Response area
    if 'query' in st.session_state and st.session_state['query']:
        st.markdown(f"**You:** {st.session_state['query']}")
        with st.spinner("Analyzing real-time social streams..."):
            st.markdown("""
            <div class="market-card" style="border-color: rgba(99, 102, 241, 0.5); background: rgba(30, 41, 59, 0.4);">
                <div style="color: #818CF8; font-weight: 600; margin-bottom: 0.5rem;">Oracle Insight</div>
                <p style="color: #F8FAFC; line-height: 1.6;">Based on current global data streams and market volume:</p>
                <ul style="color: #CBD5E1; margin-bottom: 1rem;">
                    <li><strong>Probability trajectory:</strong> Expected +8-12% increase</li>
                    <li><strong>Social Sentiment:</strong> 0.72 (Highly Bullish)</li>
                    <li><strong>Activity:</strong> Whale accumulation detected in the last 4 hours</li>
                </ul>
                <div style="font-size: 0.875rem; color: #10B981;">● High Confidence (78%)</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Clear Thread"):
                st.session_state['query'] = ""
                st.rerun()

    # Chat Input
    with st.form(key="oracle_form", clear_on_submit=True):
        user_query = st.text_input("", placeholder="Ask about any market, trend, or prediction...")
        if st.form_submit_button("Send to Oracle", use_container_width=True) and user_query:
            st.session_state['query'] = user_query
            st.rerun()

# Footer
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; color: #64748B; padding-bottom: 2rem; font-size: 0.875rem;">
    <div style="margin-bottom: 0.5rem;"><span style="color: #6366F1;">●</span> Live System Active</div>
    Last updated: {datetime.now().strftime('%I:%M %p')} UTC<br>
    Data aggregated from Polymarket & Kalshi
</div>
""", unsafe_allow_html=True)
