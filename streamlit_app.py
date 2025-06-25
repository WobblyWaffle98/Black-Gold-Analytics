import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import plotly.graph_objects as go
import re
from collections import Counter

# Page configuration
st.set_page_config(
    page_title="Black Gold Analytics", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for black and gold theme - simplified and safe
st.markdown("""
<style>
    /* Main background */
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
        font-size: 3rem;
        font-weight: 700;
        color: #ffd700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        margin: 0;
        letter-spacing: 2px;
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        color: #cccccc;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Section headers */
    .section-header {
        font-size: 2rem;
        color: #ffd700;
        margin: 2rem 0 1rem 0;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
        border: 1px solid #ffd700;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.1);
        text-align: center;
    }
    
    .content-card {
        background: linear-gradient(145deg, #1a1a1a, #252525);
        border-left: 4px solid #ffd700;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    /* Sentiment colors */
    .sentiment-bullish {
        color: #00ff88;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .sentiment-bearish {
        color: #ff4444;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* Top words */
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
    
    /* Date styling */
    .date-text {
        color: #888888;
        font-size: 0.9rem;
        font-style: italic;
    }
    
    /* Dividers */
    .gold-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #ffd700, transparent);
        margin: 2rem 0;
        border: none;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Fix for inputs */
    .stSelectbox label, .stDateInput label, .stCheckbox label {
        color: #ffffff !important;
    }
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
    'very', 's', 't', 'can', 'll', 'will', 'just', 'don', 'should', 've', 'crude',
    'production', 'demand', 'supply', 'news', 'report', 'analysis', 'week', 'day'
])

def get_top_words(text_series, stop_words, top_n=5):
    """Extract top words from text series"""
    if text_series.empty:
        return []
    
    combined_text = " ".join(text_series.dropna().astype(str)).lower()
    words = re.findall(r'\b[a-z]{3,}\b', combined_text)
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    word_counts = Counter(filtered_words)
    return word_counts.most_common(top_n)

def create_plotly_donut(sentiments, title):
    """Create enhanced donut chart with black and gold theme"""
    if sentiments.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No Data Available", 
            x=0.5, y=0.5, 
            font=dict(size=16, color="#ffd700"), 
            showarrow=False
        )
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=16, color="#ffd700"),
                x=0.5
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, b=0, l=0, r=0),
            height=350
        )
        return fig
    
    counts = sentiments.value_counts()
    labels = counts.index.tolist()
    values = counts.tolist()
    
    # Color mapping
    color_map = {
        'bearish': '#ff4444',
        'bullish': '#00ff88',
        'neutral': '#ffd700'
    }
    colors = [color_map.get(label.lower(), '#888888') for label in labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=[label.upper() for label in labels],
        values=values,
        hole=0.5,
        textinfo='label+percent',
        textfont=dict(size=11, color='white'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        marker=dict(
            colors=colors,
            line=dict(color='#ffd700', width=2)
        )
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color="#ffd700"),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=0, l=0, r=0),
        height=350,
        showlegend=False,
        font=dict(color='white')
    )
    
    return fig

def create_sentiment_timeline(df):
    """Create timeline chart using Plotly"""
    if df.empty:
        return go.Figure()
    
    # Daily sentiment counts
    daily_sentiment = df.groupby([df['Date'].dt.date, 'Sentiment V2']).size().reset_index(name='count')
    daily_sentiment['Date'] = pd.to_datetime(daily_sentiment['Date'])
    
    fig = go.Figure()
    
    # Add traces for each sentiment
    for sentiment in daily_sentiment['Sentiment V2'].unique():
        sentiment_data = daily_sentiment[daily_sentiment['Sentiment V2'] == sentiment]
        color = '#00ff88' if sentiment.lower() == 'bullish' else '#ff4444'
        
        fig.add_trace(go.Scatter(
            x=sentiment_data['Date'],
            y=sentiment_data['count'],
            mode='lines+markers',
            name=sentiment.upper(),
            line=dict(color=color, width=3),
            marker=dict(size=8, color=color, line=dict(color='white', width=1)),
            hovertemplate=f'<b>{sentiment.upper()}</b><br>Date: %{{x}}<br>Count: %{{y}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text="📈 Sentiment Timeline",
            font=dict(size=20, color="#ffd700"),
            x=0.5
        ),
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
            title="Article Count",
            title_font=dict(color="#ffd700")
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0.8)",
            bordercolor="#ffd700",
            borderwidth=1,
            font=dict(color='white')
        ),
        height=400,
        hovermode='x unified'
    )
    
    return fig

# Main application
if os.path.exists(file_path):
    try:
        df = pd.read_excel(file_path)
        df['Date'] = pd.to_datetime(df['Date'])

        # Control panel
        st.markdown('<h2 class="section-header">⚙️ Control Panel</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            min_date = df['Date'].min().date()
            max_date = df['Date'].max().date()
            default_start = max(min_date, (datetime.now() - timedelta(days=365)).date())
            
            start_date, end_date = st.date_input(
                "📅 Select Date Range:",
                value=(default_start, max_date),
                min_value=min_date,
                max_value=max_date
            )
        
        with col2:
            filter_sentiments = st.checkbox(
                "🎯 Show only Bullish and Bearish", 
                value=True
            )

        # Apply filters
        if filter_sentiments:
            df = df[df['Sentiment V2'].isin(['bullish', 'bearish'])]

        # Create filtered datasets
        df_selected = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
        df_3d = df[df['Date'] >= datetime.now() - timedelta(days=3)]
        df_7d = df[df['Date'] >= datetime.now() - timedelta(days=7)]
        df_30d = df[df['Date'] >= datetime.now() - timedelta(days=30)]

        # Sentiment distribution
        st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📊 Sentiment Distribution</h2>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        datasets = [
            (col1, df_selected, "Selected Range"),
            (col2, df_3d, "Last 3 Days"),
            (col3, df_7d, "Last 7 Days"),
            (col4, df_30d, "Last 30 Days")
        ]

        for col, data, title in datasets:
            with col:
                # Display chart
                fig = create_plotly_donut(data['Sentiment V2'], title)
                st.plotly_chart(fig, use_container_width=True)
                
                # Top words
                top_words = get_top_words(data['Reasoning'], stop_words)
                if top_words:
                    st.markdown('<div class="top-words">', unsafe_allow_html=True)
                    st.markdown("**🔤 Top Keywords:**")
                    for word, count in top_words:
                        st.markdown(f'<div class="word-item">• {word.title()} ({count})</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="top-words"><small>No keywords found</small></div>', unsafe_allow_html=True)

        # Timeline
        if not df_selected.empty:
            st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
            timeline_fig = create_sentiment_timeline(df_selected)
            st.plotly_chart(timeline_fig, use_container_width=True)

        # Summary metrics
        st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📈 Summary Metrics</h2>', unsafe_allow_html=True)
        
        if not df_selected.empty:
            total_articles = len(df_selected)
            bullish_count = len(df_selected[df_selected['Sentiment V2'].str.lower() == 'bullish'])
            bearish_count = len(df_selected[df_selected['Sentiment V2'].str.lower() == 'bearish'])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #ffd700; margin: 0;">📊 Total Articles</h3>
                    <h1 style="color: white; margin: 0.5rem 0;">{total_articles}</h1>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #00ff88; margin: 0;">📈 Bullish</h3>
                    <h1 style="color: #00ff88; margin: 0.5rem 0;">{bullish_count}</h1>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="color: #ff4444; margin: 0;">📉 Bearish</h3>
                    <h1 style="color: #ff4444; margin: 0.5rem 0;">{bearish_count}</h1>
                </div>
                """, unsafe_allow_html=True)

        # Articles section
        st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📰 Recent Articles</h2>', unsafe_allow_html=True)

        if not df_selected.empty:
            # Show recent articles (limit to 10 for performance)
            recent_articles = df_selected.sort_values('Date', ascending=False).head(10)
            
            for _, row in recent_articles.iterrows():
                sentiment_class = "sentiment-bullish" if row['Sentiment V2'].lower() == 'bullish' else "sentiment-bearish"
                
                st.markdown(f"""
                <div class="content-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                        <div style="flex: 1;">
                            <h3 style="color: #ffd700; margin: 0;">{row['Title']}</h3>
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
                    
                    {f'<p><a href="{row["Link"]}" target="_blank" style="color: #ffd700; text-decoration: none; font-weight: 500;">🔗 Read Full Article</a></p>' if pd.notna(row['Link']) else ''}
                </div>
                """, unsafe_allow_html=True)
                
                st.divider()
        else:
            st.markdown("""
            <div class="content-card">
                <p style="text-align: center; color: #888888;">No articles found for the selected criteria.</p>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

else:
    st.markdown(f"""
    <div class="content-card" style="border-left-color: #ff4444;">
        <h3 style="color: #ff4444;">❌ File Not Found</h3>
        <p>The file <code>{file_path}</code> was not found. Please ensure the file exists in the correct location.</p>
    </div>
    """, unsafe_allow_html=True)