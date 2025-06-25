import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import plotly.graph_objects as go
import plotly.express as px
import re
from collections import Counter

# Page configuration with dark theme
st.set_page_config(
    page_title="Black Gold Analytics", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for black and gold theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');
    
    /* Main background and text colors */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0f0f0f 100%);
        color: #f5f5f5;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #000000 0%, #1a1a1a 20%, #2d2d2d 50%, #1a1a1a 80%, #000000 100%);
        padding: 2rem 0;
        margin: -1rem -1rem 2rem -1rem;
        border-bottom: 3px solid #ffd700;
        text-align: center;
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.3);
    }
    
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        color: #ffd700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        margin: 0;
        letter-spacing: 2px;
    }
    
    .main-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        color: #cccccc;
        margin-top: 0.5rem;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    /* Section headers */
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        color: #ffd700;
        margin: 2rem 0 1rem 0;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
    }
    
    /* Cards and containers */
    .metric-card {
        background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
        border: 1px solid #ffd700;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .content-card {
        background: linear-gradient(145deg, #1a1a1a, #252525);
        border-left: 4px solid #ffd700;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    /* Sentiment indicators */
    .sentiment-bullish {
        color: #00ff88;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
    }
    
    .sentiment-bearish {
        color: #ff4444;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-shadow: 0 0 10px rgba(255, 68, 68, 0.3);
    }
    
    /* Top words styling */
    .top-words {
        background: rgba(255, 215, 0, 0.1);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
    
    .word-item {
        color: #ffd700;
        font-weight: 500;
        margin: 0.3rem 0;
    }
    
    /* Date and link styling */
    .date-text {
        color: #888888;
        font-size: 0.9rem;
        font-style: italic;
    }
    
    .link-button {
        background: linear-gradient(45deg, #ffd700, #ffed4e);
        color: #000000;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
        margin-top: 0.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(255, 215, 0, 0.3);
    }
    
    .link-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.5);
    }
    
    /* Dividers */
    .gold-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #ffd700, transparent);
        margin: 2rem 0;
        border: none;
    }
    
    /* Streamlit component overrides */
    .stSelectbox > div > div {
        background-color: #2d2d2d;
        border: 1px solid #ffd700;
        color: #ffffff;
    }
    
    .stDateInput > div > div {
        background-color: #2d2d2d;
        border: 1px solid #ffd700;
    }
    
    .stCheckbox > label {
        color: #ffffff;
        font-weight: 500;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header section
st.markdown("""
<div class="main-header">
    <h1 class="main-title">⚫ BLACK GOLD ANALYTICS ⚫</h1>
    <p class="main-subtitle">Advanced Sentiment Analysis Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Define file path
file_path = "sentiment_v2_updated.xlsx"

# Enhanced stop words list
stop_words = set([
    'the', 'and', 'is', 'to', 'in', 'of', 'for', 'on', 'with', 'at', 'by', 'an',
    'be', 'this', 'that', 'from', 'as', 'are', 'it', 'was', 'or', 'which', 'a',
    'because', 'oil', 'sentiment', 'prices', 'market', 'bullish', 'bearish', 
    'suggests', 'could', 'would', 'will', 'may', 'can', 'has', 'have', 'had',
    'been', 'being', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
    'may', 'might', 'must', 'shall', 'but', 'if', 'then', 'than', 'when', 'where',
    'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
    'very', 's', 't', 'can', 'll', 'will', 'just', 'don', 'should', 've'
])

def get_top_words(text_series, stop_words, top_n=5):
    """Extract top words from text series with enhanced filtering"""
    if text_series.empty:
        return []
    
    combined_text = " ".join(text_series.dropna().astype(str)).lower()
    # Enhanced regex to capture meaningful words (3+ characters)
    words = re.findall(r'\b[a-z]{3,}\b', combined_text)
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    word_counts = Counter(filtered_words)
    return word_counts.most_common(top_n)

def create_enhanced_donut(sentiments, title):
    """Create an enhanced donut chart with black and gold theme"""
    if sentiments.empty:
        # Create empty chart
        fig = go.Figure()
        fig.add_annotation(text="No Data Available", x=0.5, y=0.5, 
                          font=dict(size=20, color="#ffd700"), showarrow=False)
        fig.update_layout(
            title_text=title,
            title_font=dict(size=16, color="#ffd700", family="Playfair Display"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, b=0, l=0, r=0),
            height=300
        )
        return fig
    
    counts = sentiments.value_counts()
    labels = counts.index.tolist()
    values = counts.tolist()
    
    # Enhanced color scheme
    color_map = {
        'bearish': '#ff4444',
        'bullish': '#00ff88',
        'neutral': '#ffd700'
    }
    colors = [color_map.get(label.lower(), '#888888') for label in labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=[label.upper() for label in labels],
        values=values,
        hole=0.6,
        textinfo='label+percent',
        textfont=dict(size=12, color='white', family="Inter"),
        hoverinfo='label+value+percent',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        marker=dict(
            colors=colors,
            line=dict(color='#ffd700', width=2)
        )
    )])
    
    fig.update_layout(
        title_text=title,
        title_font=dict(size=16, color="#ffd700", family="Playfair Display"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=0, l=0, r=0),
        height=300,
        showlegend=True,
        legend=dict(
            font=dict(color="white", size=10),
            bgcolor="rgba(0,0,0,0.5)"
        )
    )
    
    return fig

def create_sentiment_timeline(df):
    """Create a timeline chart of sentiment over time"""
    if df.empty:
        return go.Figure()
    
    # Group by date and sentiment
    timeline_data = df.groupby(['Date', 'Sentiment V2']).size().reset_index(name='count')
    
    fig = go.Figure()
    
    for sentiment in timeline_data['Sentiment V2'].unique():
        sentiment_data = timeline_data[timeline_data['Sentiment V2'] == sentiment]
        color = '#00ff88' if sentiment.lower() == 'bullish' else '#ff4444' if sentiment.lower() == 'bearish' else '#ffd700'
        
        fig.add_trace(go.Scatter(
            x=sentiment_data['Date'],
            y=sentiment_data['count'],
            mode='lines+markers',
            name=sentiment.upper(),
            line=dict(color=color, width=3),
            marker=dict(size=8, color=color, line=dict(color='white', width=1))
        ))
    
    fig.update_layout(
        title="Sentiment Timeline",
        title_font=dict(size=20, color="#ffd700", family="Playfair Display"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,26,26,0.8)',
        font=dict(color='white'),
        xaxis=dict(
            gridcolor='rgba(255,215,0,0.2)',
            title="Date",
            title_font=dict(color="#ffd700")
        ),
        yaxis=dict(
            gridcolor='rgba(255,215,0,0.2)',
            title="Count",
            title_font=dict(color="#ffd700")
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0.8)",
            bordercolor="#ffd700",
            borderwidth=1
        ),
        height=400
    )
    
    return fig

# Main application logic
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    df['Date'] = pd.to_datetime(df['Date'])

    # Control panel
    st.markdown('<h2 class="section-header">⚙️ Control Panel</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Date range picker
        min_date = df['Date'].min()
        max_date = df['Date'].max()
        
        start_date, end_date = st.date_input(
            "📅 Select Date Range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    with col2:
        # Sentiment filter
        filter_sentiments = st.checkbox(
            "🎯 Show only Bullish and Bearish", value=True
        )

    # Apply filtering
    if filter_sentiments:
        df = df[df['Sentiment V2'].isin(['bullish', 'bearish'])]

    # Create filtered datasets
    df_selected = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
    df_3d = df[df['Date'] >= datetime.now() - timedelta(days=3)]
    df_7d = df[df['Date'] >= datetime.now() - timedelta(days=7)]
    df_30d = df[df['Date'] >= datetime.now() - timedelta(days=30)]

    # Sentiment distribution section
    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">📊 Sentiment Distribution</h2>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    periods = [
        (col1, df_selected, "Selected Range"),
        (col2, df_3d, "Last 3 Days"),
        (col3, df_7d, "Last 7 Days"),
        (col4, df_30d, "Last 30 Days")
    ]

    for col, data, title in periods:
        with col:
            st.plotly_chart(create_enhanced_donut(data['Sentiment V2'], title), use_container_width=True)
            
            # Top words section
            top_words = get_top_words(data['Reasoning'], stop_words)
            if top_words:
                st.markdown('<div class="top-words">', unsafe_allow_html=True)
                st.markdown("**🔤 Top Keywords:**")
                for word, count in top_words:
                    st.markdown(f'<div class="word-item">• {word.title()} ({count})</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="top-words">No keywords found</div>', unsafe_allow_html=True)

    # Timeline chart
    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">📈 Sentiment Timeline</h2>', unsafe_allow_html=True)
    
    if not df_selected.empty:
        timeline_fig = create_sentiment_timeline(df_selected)
        st.plotly_chart(timeline_fig, use_container_width=True)

    # Articles section
    st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">📰 Article Analysis</h2>', unsafe_allow_html=True)

    if not df_selected.empty:
        filtered_df = df_selected[['Date', 'Title', 'Sentiment V2', 'Link', 'Reasoning']].sort_values('Date', ascending=False)
        
        # Summary stats
        total_articles = len(filtered_df)
        bullish_count = len(filtered_df[filtered_df['Sentiment V2'].str.lower() == 'bullish'])
        bearish_count = len(filtered_df[filtered_df['Sentiment V2'].str.lower() == 'bearish'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><h3 style="color: #ffd700;">📊 Total Articles</h3><h2 style="color: white;">{total_articles}</h2></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><h3 style="color: #00ff88;">📈 Bullish</h3><h2 style="color: #00ff88;">{bullish_count}</h2></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><h3 style="color: #ff4444;">📉 Bearish</h3><h2 style="color: #ff4444;">{bearish_count}</h2></div>', unsafe_allow_html=True)

        # Articles list
        for _, row in filtered_df.iterrows():
            sentiment_class = "sentiment-bullish" if row['Sentiment V2'].lower() == 'bullish' else "sentiment-bearish"
            
            st.markdown(f"""
            <div class="content-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div style="flex: 1;">
                        <h3 style="color: #ffd700; margin: 0; font-family: 'Playfair Display', serif;">{row['Title']}</h3>
                        <p class="date-text">📅 {row['Date'].strftime('%B %d, %Y')}</p>
                    </div>
                    <div style="margin-left: 1rem;">
                        <span class="{sentiment_class}">● {row['Sentiment V2'].upper()}</span>
                    </div>
                </div>
                
                <div style="margin: 1rem 0;">
                    <h4 style="color: #ffd700; margin-bottom: 0.5rem;">🧠 Analysis:</h4>
                    <p style="color: #cccccc; line-height: 1.6;">{row['Reasoning']}</p>
                </div>
                
                {f'<a href="{row["Link"]}" target="_blank" class="link-button">🔗 Read Full Article</a>' if pd.notna(row['Link']) else ''}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="content-card"><p style="text-align: center; color: #888888;">No articles found for the selected criteria.</p></div>', unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div class="content-card" style="border-left-color: #ff4444;">
        <h3 style="color: #ff4444;">❌ File Not Found</h3>
        <p>The file <code>{file_path}</code> was not found. Please ensure the file exists in the correct location.</p>
    </div>
    """, unsafe_allow_html=True)