import streamlit as st
import pandas as pd
import plotly.express as px
from fetcher import get_all_markets
from sentiment import calculate_sentiment, get_category_sentiment

# Page config
st.set_page_config(
    page_title="PulseRadar",
    page_icon="📡",
    layout="wide"
)

# Title
st.title("🌍 PulseRadar")
st.caption("Real-time sentiment from prediction markets")

# Sidebar
st.sidebar.header("Controls")
refresh = st.sidebar.button("🔄 Refresh Data")
limit = st.sidebar.slider("Markets", 10, 100, 50)

# Load data
if refresh or 'df' not in st.session_state:
    with st.spinner("Fetching markets..."):
        raw_df = get_all_markets(limit)
        if not raw_df.empty:
            df = calculate_sentiment(raw_df)
            st.session_state.df = df
        else:
            st.error("Could not fetch data. Using sample data.")
            # Sample data as fallback
            sample_data = {
                'question': ['Will Trump win?', 'Bitcoin $100K?', 'Fed rate cut?'],
                'category': ['Politics', 'Crypto', 'Macro'],
                'yes_price': [0.65, 0.45, 0.70],
                'volume': [1000000, 500000, 750000],
                'source': ['Polymarket', 'Polymarket', 'Polymarket']
            }
            df = calculate_sentiment(pd.DataFrame(sample_data))
            st.session_state.df = df

df = st.session_state.df

# Tabs
tab1, tab2 = st.tabs(["📊 Markets", "📈 Sentiment"])

with tab1:
    st.subheader("Live Markets")
    
    # Display
    display_df = df[['question', 'category', 'yes_price', 'volume', 'source']].copy()
    display_df['yes_price'] = display_df['yes_price'].apply(lambda x: f"{x:.1%}")
    display_df['volume'] = display_df['volume'].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(
        display_df,
        column_config={
            "question": "Market",
            "category": "Category",
            "yes_price": "Yes Probability",
            "volume": "Volume",
            "source": "Platform"
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Volume chart
    fig = px.bar(
        df.head(10),
        x='question',
        y='volume',
        color='category',
        title="Top 10 Markets by Volume"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Sentiment by Category")
    
    sentiment_df = get_category_sentiment(df)
    
    if not sentiment_df.empty:
        # Color-coded dataframe
        styled = sentiment_df.style.format({
            'Sentiment': '{:.3f}',
            'Markets': '{:.0f}'
        }).background_gradient(
            subset=['Sentiment'],
            cmap='RdYlGn',
            vmin=0,
            vmax=1
        )
        
        st.dataframe(styled, use_container_width=True, hide_index=True)
        
        # Sentiment chart
        fig2 = px.bar(
            sentiment_df[sentiment_df['Category'] != 'OVERALL'],
            x='Category',
            y='Sentiment',
            color='Sentiment',
            color_continuous_scale='RdYlGn',
            range_color=[0, 1],
            title="Sentiment by Category"
        )
        fig2.add_hline(y=0.5, line_dash="dash", line_color="gray")
        st.plotly_chart(fig2, use_container_width=True)
        
        # Key metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            overall = sentiment_df[sentiment_df['Category'] == 'OVERALL'].iloc[0]
            st.metric("Overall Sentiment", f"{overall['Sentiment']:.3f}")
        with col2:
            st.metric("Total Markets", overall['Markets'])
        with col3:
            st.metric("Total Volume", overall['Volume'])
    else:
        st.warning("No sentiment data available")

# Footer
st.markdown("---")
st.caption("Data from Polymarket • Updates on refresh")
