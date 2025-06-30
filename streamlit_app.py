import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import plotly.graph_objects as go
import plotly.express as px
import re
from collections import Counter

# Enhanced CSS with modern design elements
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root variables */
    :root {
        --gold-primary: #D4AF37;
        --gold-secondary: #F4D03F;
        --gold-accent: #FFE135;
        --black-primary: #0B0B0F;
        --black-secondary: #1A1A1E;
        --gray-dark: #2A2A30;
        --gray-medium: #404047;
        --gray-light: #8B8B93;
        --white: #FFFFFF;
        --success: #10B981;
        --danger: #EF4444;
        --shadow-gold: rgba(212, 175, 55, 0.15);
        --shadow-dark: rgba(0, 0, 0, 0.25);
    }

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main app styling */
    .stApp {
        background: radial-gradient(ellipse at top, #1A1A1E 0%, #0B0B0F 100%);
        color: var(--white);
    }

    .main .block-container {
        padding: 1rem 2rem 3rem;
        max-width: 1400px;
        margin: 0 auto;
    }

    /* Enhanced title */
    .hero-section {
        text-align: center;
        padding: 3rem 0 4rem;
        background: linear-gradient(135deg, transparent 0%, rgba(212, 175, 55, 0.03) 50%, transparent 100%);
        border-radius: 20px;
        margin-bottom: 3rem;
        position: relative;
        overflow: hidden;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 50% 50%, rgba(212, 175, 55, 0.08) 0%, transparent 70%);
        pointer-events: none;
    }

    .main-title {
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 700;
        background: linear-gradient(135deg, #D4AF37 0%, #F4D03F 50%, #FFE135 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }

    .subtitle {
        color: var(--gray-light);
        font-size: 1.1rem;
        margin-top: 1rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }

    /* Modern section headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        color: var(--white);
        font-size: 1.5rem;
        font-weight: 600;
        margin: 3rem 0 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
        position: relative;
    }

    .section-header::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, var(--gold-primary), transparent);
    }

    /* Glassmorphism cards */
    .glass-card {
        background: rgba(26, 26, 30, 0.7);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 
            0 8px 32px var(--shadow-dark),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.05), transparent);
        transition: left 0.6s ease;
    }

    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(212, 175, 55, 0.3);
        box-shadow: 
            0 12px 48px var(--shadow-dark),
            0 0 24px var(--shadow-gold),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    .glass-card:hover::before {
        left: 100%;
    }

    /* Enhanced metrics grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }

    .metric-item {
        background: rgba(26, 26, 30, 0.8);
        border: 1px solid rgba(212, 175, 55, 0.15);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .metric-item::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--gold-primary), var(--gold-secondary));
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }

    .metric-item:hover::after {
        transform: scaleX(1);
    }

    /* Modern sidebar */
    .css-1d391kg, .css-1cypcdb {
        background: linear-gradient(180deg, rgba(26, 26, 30, 0.95) 0%, rgba(11, 11, 15, 0.95) 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(212, 175, 55, 0.1);
    }

    .sidebar-header {
        color: var(--gold-primary);
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    }

    /* Enhanced form controls */
    .stDateInput > label, .stCheckbox > label {
        color: var(--gold-primary) !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }

    .stDateInput input {
        background: rgba(26, 26, 30, 0.8) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 8px !important;
        color: var(--white) !important;
    }

    /* News feed enhancements */
    .news-item {
        background: rgba(26, 26, 30, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-left: 4px solid var(--gold-primary);
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .news-item::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at top left, rgba(212, 175, 55, 0.03) 0%, transparent 50%);
        pointer-events: none;
    }

    .news-item:hover {
        transform: translateY(-4px) translateX(8px);
        border-color: rgba(212, 175, 55, 0.3);
        box-shadow: 
            -8px 16px 32px var(--shadow-dark),
            0 0 24px var(--shadow-gold);
    }

    .news-title {
        color: var(--white);
        font-size: 1.2rem;
        font-weight: 600;
        line-height: 1.4;
        margin-bottom: 1rem;
    }

    .news-meta {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }

    .news-date {
        color: var(--gray-light);
        font-size: 0.9rem;
        font-weight: 400;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Premium sentiment badges */
    .sentiment-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        border: 1px solid transparent;
    }

    .sentiment-bullish {
        background: linear-gradient(135deg, var(--success) 0%, #059669 100%);
        color: white;
        border-color: rgba(16, 185, 129, 0.3);
    }

    .sentiment-bearish {
        background: linear-gradient(135deg, var(--danger) 0%, #DC2626 100%);
        color: white;
        border-color: rgba(239, 68, 68, 0.3);
    }

    /* Enhanced action button */
    .news-link {
        background: linear-gradient(135deg, var(--gold-primary) 0%, var(--gold-secondary) 100%);
        color: var(--black-primary) !important;
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        text-decoration: none !important;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
        border: 1px solid rgba(212, 175, 55, 0.5);
    }

    .news-link:hover {
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 8px 24px rgba(212, 175, 55, 0.4);
        background: linear-gradient(135deg, var(--gold-secondary) 0%, var(--gold-accent) 100%);
    }

    /* Analysis section */
    .reasoning-section {
        background: rgba(212, 175, 55, 0.05);
        border: 1px solid rgba(212, 175, 55, 0.15);
        border-left: 3px solid var(--gold-primary);
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        position: relative;
    }

    .reasoning-header {
        color: var(--gold-primary);
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .reasoning-text {
        color: #E5E5E7;
        line-height: 1.6;
        font-size: 0.95rem;
    }

    /* Word tags */
    .top-words-container {
        margin-top: 1.5rem;
    }

    .word-tag {
        background: rgba(42, 42, 48, 0.8);
        color: var(--gold-primary);
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        margin: 0.25rem 0.25rem 0.25rem 0;
        display: inline-flex;
        align-items: center;
        font-size: 0.85rem;
        font-weight: 500;
        border: 1px solid rgba(212, 175, 55, 0.2);
        transition: all 0.3s ease;
    }

    .word-tag:hover {
        background: rgba(212, 175, 55, 0.1);
        border-color: rgba(212, 175, 55, 0.4);
        transform: scale(1.05);
    }

    /* Loading states */
    .loading-shimmer {
        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.1), transparent);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
    }

    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .news-item {
            padding: 1.5rem;
        }
        
        .news-meta {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(42, 42, 48, 0.5);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(212, 175, 55, 0.5);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(212, 175, 55, 0.7);
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="Black Gold Analytics",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hero section
st.markdown('''
<div class="hero-section">
    <h1 class="main-title">🛢️ BLACK GOLD ANALYTICS</h1>
    <p class="subtitle">Premium Market Intelligence & Sentiment Analysis</p>
</div>
''', unsafe_allow_html=True)

# Define file path
file_path = "sentiment_v2_updated.xlsx"

# Enhanced stop words
stop_words = set([
    'the', 'and', 'is', 'to', 'in', 'of', 'for', 'on', 'with', 'at', 'by', 'an',
    'be', 'this', 'that', 'from', 'as', 'are', 'it', 'was', 'or', 'which', 'a',
    'because', 'oil', 'sentiment', 'prices', 'market', 'bullish', 'suggests', 'could',
    'will', 'may', 'can', 'would', 'should', 'might', 'has', 'have', 'had', 'been',
    'than', 'more', 'most', 'some', 'any', 'also', 'other', 'such', 'only', 'own',
    'out', 'so', 'her', 'there', 'what', 'up', 'its', 'about', 'into', 'them'
])

def get_top_words(text_series, stop_words, top_n=5):
    """Extract top words from text series with enhanced filtering"""
    combined_text = " ".join(text_series.dropna().astype(str)).lower()
    words = re.findall(r'\b[a-z]+\b', combined_text)
    filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
    word_counts = Counter(filtered_words)
    return word_counts.most_common(top_n)

def create_enhanced_donut(sentiments, title):
    """Create modern donut chart with enhanced styling"""
    counts = sentiments.value_counts()
    labels = counts.index.tolist()
    values = counts.tolist()

    # Enhanced color mapping
    color_map = {
        'bearish': '#EF4444',
        'bullish': '#10B981',
        'neutral': '#6B7280'
    }
    colors = [color_map.get(label, '#6B7280') for label in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        textinfo='label+percent',
        textfont=dict(size=12, color='white'),
        hoverinfo='label+value+percent',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        marker=dict(
            colors=colors,
            line=dict(color='rgba(255,255,255,0.2)', width=2)
        )
    )])

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=16, color='#D4AF37'),
            x=0.5
        ),
        font=dict(color='white'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=20, l=20, r=20),
        height=300,
        showlegend=False
    )
    
    return fig

# Check if data file exists
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    df['Date'] = pd.to_datetime(df['Date'])

    # Enhanced sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-header">⚙️ CONTROL PANEL</div>', unsafe_allow_html=True)
        
        # Date range picker
        min_date = df['Date'].min()
        max_date = df['Date'].max()
        
        st.markdown("**📅 Date Range**")
        start_date, end_date = st.date_input(
            "Select analysis period:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("**🎯 Analysis Filters**")
        filter_sentiments = st.checkbox(
            "Focus on Bullish/Bearish only", 
            value=True,
            help="Filter out neutral sentiment for clearer analysis"
        )
        
        st.markdown("---")
        st.markdown("**📊 Quick Stats**")
        total_articles = len(df)
        bullish_count = len(df[df['Sentiment V2'] == 'bullish'])
        bearish_count = len(df[df['Sentiment V2'] == 'bearish'])
        
        st.metric("Total Articles", f"{total_articles:,}")
        st.metric("Bullish Sentiment", f"{bullish_count:,}")
        st.metric("Bearish Sentiment", f"{bearish_count:,}")

    # Apply filtering
    if filter_sentiments:
        df = df[df['Sentiment V2'].isin(['bullish', 'bearish'])]

    # Create filtered datasets
    df_selected = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
    df_3d = df[df['Date'] >= datetime.now() - timedelta(days=3)]
    df_7d = df[df['Date'] >= datetime.now() - timedelta(days=7)]
    df_30d = df[df['Date'] >= datetime.now() - timedelta(days=30)]

    # Enhanced metrics section
    st.markdown('<div class="section-header">📊 SENTIMENT DASHBOARD</div>', unsafe_allow_html=True)
    
    # Create enhanced metrics grid
    col1, col2, col3, col4 = st.columns(4)
    
    datasets = [
        (df_selected, "Selected Range", col1),
        (df_3d, "Last 3 Days", col2),
        (df_7d, "Last 7 Days", col3),
        (df_30d, "Last 30 Days", col4)
    ]
    
    for data, period, col in datasets:
        with col:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            # Enhanced chart
            if len(data) > 0:
                fig = create_enhanced_donut(data['Sentiment V2'], period)
                st.plotly_chart(fig, use_container_width=True)
                
                # Top words with enhanced styling
                top_words = get_top_words(data['Reasoning'], stop_words)
                if top_words:
                    st.markdown('<div class="top-words-container">', unsafe_allow_html=True)
                    for word, count in top_words:
                        st.markdown(f'<span class="word-tag">{word} ({count})</span>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="text-align: center; padding: 2rem; color: #8B8B93;">No data available for {period.lower()}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Enhanced news feed
    st.markdown('<div class="section-header">📰 MARKET INTELLIGENCE FEED</div>', unsafe_allow_html=True)
    
    filtered_df = df_selected[['Date', 'Title', 'Sentiment V2', 'Link', 'Reasoning']].sort_values('Date', ascending=False)
    
    if len(filtered_df) == 0:
        st.markdown('''
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <h3 style="color: #8B8B93; margin-bottom: 1rem;">📭 No Data Available</h3>
            <p style="color: #8B8B93;">No articles found for the selected date range. Try adjusting your filters.</p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        for idx, row in filtered_df.iterrows():
            sentiment_class = f"sentiment-{row['Sentiment V2']}" if row['Sentiment V2'] in ['bullish', 'bearish'] else 'sentiment-neutral'
            sentiment_icon = "📈" if row['Sentiment V2'] == 'bullish' else "📉" if row['Sentiment V2'] == 'bearish' else "➖"
            
            news_html = f'''
            <div class="news-item">
                <div class="news-title">{row['Title']}</div>
                <div class="news-meta">
                    <div class="news-date">
                        <span>📅</span>
                        {row['Date'].strftime('%B %d, %Y at %I:%M %p')}
                    </div>
                    <div class="sentiment-badge {sentiment_class}">
                        <span>{sentiment_icon}</span>
                        {row['Sentiment V2'].upper()}
                    </div>
                </div>
            '''
            
            if pd.notna(row['Link']):
                news_html += f'''
                <a href="{row["Link"]}" class="news-link" target="_blank">
                    <span>🔗</span>
                    Read Full Article
                </a>
                '''
            
            news_html += f'''
                <div class="reasoning-section">
                    <div class="reasoning-header">
                        <span>🧠</span>
                        AI Analysis
                    </div>
                    <div class="reasoning-text">{row['Reasoning']}</div>
                </div>
            </div>
            '''
            
            st.markdown(news_html, unsafe_allow_html=True)

else:
    # Enhanced error state
    st.markdown('''
    <div class="glass-card" style="text-align: center; padding: 3rem;">
        <h2 style="color: #EF4444; margin-bottom: 1rem;">❌ Data Source Unavailable</h2>
        <p style="color: #8B8B93; font-size: 1.1rem;">The sentiment data file could not be located.</p>
        <p style="color: #8B8B93;">Please ensure <code>sentiment_v2_updated.xlsx</code> is available in the application directory.</p>
    </div>
    ''', unsafe_allow_html=True)

# Enhanced footer
st.markdown("---")
st.markdown('''
<div style="text-align: center; padding: 2rem; color: #8B8B93;">
    <p style="margin-bottom: 0.5rem;">© 2024 Black Gold Analytics</p>
    <p style="font-size: 0.9rem; opacity: 0.8;">Premium Market Intelligence & Sentiment Analysis Platform</p>
</div>
''', unsafe_allow_html=True)