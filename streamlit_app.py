import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import plotly.graph_objects as go
import plotly.express as px
import re
from collections import Counter

# Custom CSS for black and gold theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-gold: #FFD700;
        --secondary-gold: #FFC107;
        --dark-gold: #B8860B;
        --rich-black: #0A0A0A;
        --charcoal: #1A1A1A;
        --dark-gray: #2D2D2D;
        --light-gray: #B0B0B0;
        --accent-gold: #F4D03F;
    }

    /* App background */
    .stApp {
        background: linear-gradient(135deg, #0A0A0A 0%, #1A1A1A 100%);
        color: #FFFFFF;
    }

    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }

    /* Title styling */
    .main-title {
        background: linear-gradient(45deg, #FFD700, #FFC107);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(255, 215, 0, 0.3);
    }

    /* Section headers */
    .section-header {
        color: #FFD700;
        font-size: 1.5rem;
        font-weight: 600;
        border-bottom: 2px solid #FFD700;
        padding-bottom: 0.5rem;
        margin: 1.5rem 0;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 100%);
        border: 1px solid #FFD700;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.2);
    }

    /* Custom checkbox */
    .stCheckbox > label {
        color: #FFD700 !important;
        font-weight: 500;
    }

    /* Date input styling */
    .stDateInput > label {
        color: #FFD700 !important;
        font-weight: 500;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1A1A1A 0%, #2D2D2D 100%);
    }

    /* News item styling */
    .news-item {
        background: linear-gradient(135deg, #1A1A1A 0%, #252525 100%);
        border-left: 4px solid #FFD700;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .news-item:hover {
        background: linear-gradient(135deg, #252525 0%, #2D2D2D 100%);
        transform: translateX(5px);
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.1);
    }

    .news-title {
        color: #FFFFFF;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .news-date {
        color: #B0B0B0;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }

    .news-link {
        background: linear-gradient(45deg, #FFD700, #FFC107);
        color: #000000 !important;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        text-decoration: none !important;
        font-weight: 500;
        display: inline-block;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }

    .news-link:hover {
        background: linear-gradient(45deg, #FFC107, #B8860B);
        transform: scale(1.05);
    }

    .sentiment-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }

    .sentiment-bullish {
        background: linear-gradient(45deg, #2E8B57, #228B22);
        color: white;
        box-shadow: 0 2px 8px rgba(46, 139, 87, 0.3);
    }

    .sentiment-bearish {
        background: linear-gradient(45deg, #DC143C, #B22222);
        color: white;
        box-shadow: 0 2px 8px rgba(220, 20, 60, 0.3);
    }

    .reasoning-text {
        background: rgba(255, 215, 0, 0.05);
        border-left: 3px solid #FFD700;
        padding: 1rem;
        border-radius: 5px;
        margin-top: 1rem;
        font-style: italic;
        color: #E0E0E0;
    }

    /* Top words styling */
    .top-words {
        background: rgba(255, 215, 0, 0.05);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
    }

    .word-item {
        background: linear-gradient(45deg, #2D2D2D, #3D3D3D);
        color: #FFD700;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        margin: 0.2rem 0;
        display: inline-block;
        font-weight: 500;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="Black Gold Analytics",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Main title with custom styling
st.markdown('<h1 class="main-title">🛢️ BLACK GOLD ANALYTICS</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #B0B0B0; font-size: 1.2rem; margin-bottom: 2rem;">Premium Oil Market Sentiment Intelligence</p>', unsafe_allow_html=True)

# Define file path
file_path = "sentiment_v2_updated.xlsx"

# Enhanced stop words
stop_words = set([
    'the', 'and', 'is', 'to', 'in', 'of', 'for', 'on', 'with', 'at', 'by', 'an',
    'be', 'this', 'that', 'from', 'as', 'are', 'it', 'was', 'or', 'which', 'a',
    'because', 'oil', 'sentiment', 'prices', 'market', 'bullish', 'suggests', 'could',
    'will', 'may', 'can', 'would', 'should', 'might', 'has', 'have', 'had', 'been',
    'than', 'more', 'most', 'some', 'any', 'also', 'other', 'such', 'only', 'own',
    'out', 'so', 'can', 'her', 'there', 'what', 'up', 'its', 'about', 'into', 'than', 'them'
])

def get_top_words(text_series, stop_words, top_n=5):
    combined_text = " ".join(text_series.dropna().astype(str)).lower()
    words = re.findall(r'\b[a-z]+\b', combined_text)
    filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
    word_counts = Counter(filtered_words)
    return word_counts.most_common(top_n)

def create_modern_donut(sentiments, title):
    """Create a modern donut chart with black and gold theme"""
    counts = sentiments.value_counts()
    labels = counts.index.tolist()
    values = counts.tolist()
    
    # Custom colors for sentiment
    color_map = {
        'bearish': '#DC143C',
        'bullish': '#228B22'
    }
    colors = [color_map.get(label, '#FFD700') for label in labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        textinfo='label+percent',
        textfont=dict(size=14, color='white', family='Arial Black'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        marker=dict(
            colors=colors,
            line=dict(color='#FFD700', width=2)
        ),
        pull=[0.05 if label == 'bullish' else 0.02 for label in labels]
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='#FFD700', family='Arial Black'),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=20, l=20, r=20),
        height=300,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color='white', size=12)
        )
    )
    
    return fig

if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    df['Date'] = pd.to_datetime(df['Date'])

    # Sidebar for controls
    with st.sidebar:
        st.markdown('<h2 style="color: #FFD700;">⚙️ CONTROLS</h2>', unsafe_allow_html=True)
        
        # Date range picker
        min_date = df['Date'].min()
        max_date = df['Date'].max()
        
        st.markdown("**📅 Date Range**")
        start_date, end_date = st.date_input(
            "Select date range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed"
        )
        
        st.markdown("**🎯 Filters**")
        filter_sentiments = st.checkbox(
            "Show only Bullish and Bearish sentiment", 
            value=True
        )

    # Apply filtering
    if filter_sentiments:
        df = df[df['Sentiment V2'].isin(['bullish', 'bearish'])]

    # Create filtered datasets
    df_selected = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
    df_3d = df[df['Date'] >= datetime.now() - timedelta(days=3)]
    df_7d = df[df['Date'] >= datetime.now() - timedelta(days=7)]
    df_30d = df[df['Date'] >= datetime.now() - timedelta(days=30)]

    # Key metrics section
    st.markdown('<div class="section-header">📊 SENTIMENT OVERVIEW</div>', unsafe_allow_html=True)
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    datasets = [
        (df_selected, "Selected Range", col1),
        (df_3d, "Last 3 Days", col2),
        (df_7d, "Last 7 Days", col3),
        (df_30d, "Last 30 Days", col4)
    ]
    
    for data, period, col in datasets:
        with col:
            # Chart
            fig = create_modern_donut(data['Sentiment V2'], period)
            st.plotly_chart(fig, use_container_width=True)
            
            # Top words
            top_words = get_top_words(data['Reasoning'], stop_words)
            if top_words:
                st.markdown(f'<div class="top-words"><strong style="color: #FFD700;">🔑 Key Terms</strong><br>', unsafe_allow_html=True)
                for word, count in top_words:
                    st.markdown(f'<span class="word-item">{word} ({count})</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # News feed section
    st.markdown('<div class="section-header">📰 SENTIMENT ANALYSIS FEED</div>', unsafe_allow_html=True)
    
    filtered_df = df_selected[['Date', 'Title', 'Sentiment V2', 'Link', 'Reasoning']].sort_values('Date', ascending=False)
    
    if len(filtered_df) == 0:
        st.markdown('<div style="text-align: center; color: #B0B0B0; padding: 2rem;">No data available for the selected date range.</div>', unsafe_allow_html=True)
    else:
        for _, row in filtered_df.iterrows():
            sentiment_class = f"sentiment-{row['Sentiment V2']}" if row['Sentiment V2'] in ['bullish', 'bearish'] else 'sentiment-neutral'
            
            news_html = f'''
            <div class="news-item">
                <div class="news-title">{row['Title']}</div>
                <div class="news-date">📅 {row['Date'].strftime('%B %d, %Y')}</div>
                <div style="margin: 1rem 0;">
                    <span class="sentiment-badge {sentiment_class}">{row['Sentiment V2'].upper()}</span>
                </div>
            '''
            
            if pd.notna(row['Link']):
                news_html += f'<a href="{row["Link"]}" class="news-link" target="_blank">🔗 Read Full Article</a>'
            
            news_html += f'''
                <div class="reasoning-text">
                    <strong style="color: #FFD700;">💡 Analysis:</strong><br>
                    {row['Reasoning']}
                </div>
            </div>
            '''
            
            st.markdown(news_html, unsafe_allow_html=True)

else:
    st.error(f"❌ Data file not found: {file_path}")
    st.markdown("Please ensure the sentiment data file is available in the application directory.")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #B0B0B0; padding: 1rem;">© 2024 Black Gold Analytics - Premium Market Intelligence</div>',
    unsafe_allow_html=True
)