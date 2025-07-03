import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import re
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import yfinance as yf
from plotly.subplots import make_subplots

# Custom CSS for black and gold theme with compact news layout
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

    /* COMPACT NEWS ITEM STYLING */
    .news-item {
        background: linear-gradient(135deg, #1A1A1A 0%, #252525 100%);
        border-left: 3px solid #FFD700;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 5px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
        position: relative;
    }

    .news-item:hover {
        background: linear-gradient(135deg, #252525 0%, #2D2D2D 100%);
        transform: translateX(3px);
        box-shadow: 0 2px 10px rgba(255, 215, 0, 0.1);
    }

    .news-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.5rem;
        gap: 1rem;
    }

    .news-title {
        color: #FFFFFF;
        font-size: 1rem;
        font-weight: 600;
        line-height: 1.3;
        flex: 1;
        margin: 0;
    }

    .news-meta {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        flex-shrink: 0;
    }

    .news-date {
        color: #B0B0B0;
        font-size: 0.8rem;
        white-space: nowrap;
    }

    .news-link {
        background: linear-gradient(45deg, #FFD700, #FFC107);
        color: #000000 !important;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        text-decoration: none !important;
        font-weight: 500;
        font-size: 0.8rem;
        transition: all 0.2s ease;
        white-space: nowrap;
    }

    .news-link:hover {
        background: linear-gradient(45deg, #FFC107, #B8860B);
        transform: scale(1.03);
    }

    .category-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-weight: bold;
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 0.3px;
        min-width: 60px;
        text-align: center;
        background: linear-gradient(45deg, #4A90E2, #357ABD);
        color: white;
        box-shadow: 0 1px 4px rgba(74, 144, 226, 0.3);
    }

    .sentiment-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-weight: bold;
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 0.3px;
        min-width: 60px;
        text-align: center;
    }

    .sentiment-bullish {
        background: linear-gradient(45deg, #2E8B57, #228B22);
        color: white;
        box-shadow: 0 1px 4px rgba(46, 139, 87, 0.3);
    }

    .sentiment-bearish {
        background: linear-gradient(45deg, #DC143C, #B22222);
        color: white;
        box-shadow: 0 1px 4px rgba(220, 20, 60, 0.3);
    }

    .reasoning-text {
        background: rgba(255, 215, 0, 0.03);
        border-left: 2px solid rgba(255, 215, 0, 0.3);
        padding: 0.6rem;
        border-radius: 4px;
        margin-top: 0.5rem;
        font-style: italic;
        color: #D0D0D0;
        font-size: 0.9rem;
        line-height: 1.4;
    }

    .reasoning-label {
        color: #FFD700;
        font-weight: 600;
        font-size: 0.8rem;
        margin-bottom: 0.3rem;
        display: block;
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

    /* Connection status */
    .connection-status {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-weight: 500;
    }

    .connection-success {
        background: rgba(46, 139, 87, 0.2);
        border: 1px solid #2E8B57;
        color: #90EE90;
    }

    .connection-error {
        background: rgba(220, 20, 60, 0.2);
        border: 1px solid #DC143C;
        color: #FFB6C1;
    }

    /* Responsive design for mobile */
    @media (max-width: 768px) {
        .news-header {
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .news-meta {
            align-self: flex-start;
        }
        
        .news-title {
            font-size: 0.95rem;
        }
    }
            
    /* Refresh button styling */
    .refresh-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        background: linear-gradient(45deg, #FFD700, #FFC107);
        color: #000000;
        border: none;
        border-radius: 50px;
        padding: 12px 20px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .refresh-button:hover {
        background: linear-gradient(45deg, #FFC107, #B8860B);
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
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

# MongoDB connection configuration
uri = st.secrets.db_credentials.url

# Load data from MongoDB
@st.cache_data()  # Cache for 5 minutes
def load_data():
    client = MongoClient(uri, server_api=ServerApi('1'))
    if client is None:
        return pd.DataFrame()
    
    try:
        db = client['blackgold_db']
        collection = db['rss_articles']
        
        # Fetch all documents
        cursor = collection.find({})
        data = list(cursor)
        
        if not data:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Clean and prepare data
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Handle different sentiment column names
        if 'Sentiment V2' in df.columns:
            df['Sentiment'] = df['Sentiment V2']
        elif 'Sentiment' not in df.columns:
            df['Sentiment'] = 'neutral'
        
        # Ensure Category column exists
        if 'Category' not in df.columns:
            df['Category'] = 'General'
        
        # Ensure Reasoning column exists
        if 'Reasoning' not in df.columns:
            df['Reasoning'] = 'Analysis pending'
        
        # Filter out rows with invalid dates
        df = df.dropna(subset=['Date'])
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data from MongoDB: {e}")
        return pd.DataFrame()

# Load Brent crude oil price data
@st.cache_data()
def load_brent_data(start_date, end_date):
    try:
        # Fetch Brent crude oil data (ticker: BZ=F)
        brent = yf.download('BZ=F', start=start_date, end=end_date, progress=False)
        if brent.empty:
            return pd.DataFrame()
        
        # Reset index to get date as column
        brent = brent.reset_index()
        brent['Date'] = pd.to_datetime(brent['Date'])
        
        return brent
    except Exception as e:
        st.error(f"Error loading Brent data: {e}")
        return pd.DataFrame()

# Add refresh functionality
def refresh_data():
    """Clear cache and reload data"""
    load_data.clear()
    load_brent_data.clear()
    st.rerun()

# Enhanced stop words
try:
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

# Custom stop words
custom_stop_words = set([
    'oil', 'sentiment', 'prices', 'market', 'bullish', 'suggests',
    'could', 'will', 'may', 'can', 'would', 'should', 'might'
])

try:
    stop_words = set(stopwords.words('english')).union(custom_stop_words)
except:
    stop_words = custom_stop_words

def preprocess(text):
    try:
        lemmatizer = WordNetLemmatizer()
        text = str(text).lower()
        tokens = re.findall(r'\b[a-z]+\b', text)
        return ' '.join([lemmatizer.lemmatize(token) for token in tokens if token not in stop_words and len(token) > 2])
    except:
        return str(text).lower()

def get_top_phrases(text_series, stop_words, top_n=5, ngram_range=(1, 2)):
    try:
        cleaned = text_series.dropna().astype(str).apply(preprocess)
        if len(cleaned) == 0:
            return []
        
        vectorizer = CountVectorizer(stop_words=list(stop_words), ngram_range=ngram_range)
        X = vectorizer.fit_transform(cleaned)
        sum_words = X.sum(axis=0)
        words_freq = [(word, int(sum_words[0, idx])) for word, idx in vectorizer.vocabulary_.items()]
        sorted_words = sorted(words_freq, key=lambda x: x[1], reverse=True)
        return sorted_words[:top_n]
    except:
        return []

def plotly_donut(sentiments, title):
    if len(sentiments) == 0:
        # Create empty chart
        fig = go.Figure(data=[go.Pie(labels=[], values=[])])
        fig.update_layout(title_text=f"{title} - No Data", margin=dict(t=40, b=0, l=0, r=0), 
                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig
    
    counts = sentiments.value_counts()
    labels = counts.index.tolist()
    values = counts.tolist()

    # Define custom colors
    color_map = {
        'bearish': 'darkred',
        'bullish': 'darkgreen',
        'neutral': 'gray'
    }
    colors = [color_map.get(label, 'lightblue') for label in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        textinfo='label+percent',
        hoverinfo='label+value',
        marker=dict(colors=colors)
    )])
    fig.update_layout(title_text=title, margin=dict(t=40, b=0, l=0, r=0), 
                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def create_net_sentiment_with_brent_chart(df, brent_data, title="Net Sentiment and Brent Crude Oil Price"):
    """Create a subplot chart showing net sentiment and Brent crude oil price separately"""

    # Create subplots: 2 rows, 1 column
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Net Sentiment", "Brent Crude Oil Price ($USD)")
    )

    if len(df) > 0:
        # Group by date and sentiment, count occurrences
        daily_sentiment = df.groupby([df['Date'].dt.date, 'Sentiment']).size().unstack(fill_value=0)

        # Calculate net sentiment (bullish - bearish)
        if 'bullish' in daily_sentiment.columns and 'bearish' in daily_sentiment.columns:
            daily_sentiment['net_sentiment'] = daily_sentiment['bullish'] - daily_sentiment['bearish']
        elif 'bullish' in daily_sentiment.columns:
            daily_sentiment['net_sentiment'] = daily_sentiment['bullish']
        elif 'bearish' in daily_sentiment.columns:
            daily_sentiment['net_sentiment'] = -daily_sentiment['bearish']
        else:
            daily_sentiment['net_sentiment'] = 0

        colors = ['darkgreen' if x >= 0 else 'darkred' for x in daily_sentiment['net_sentiment']]

        fig.add_trace(go.Bar(
            x=daily_sentiment.index,
            y=daily_sentiment['net_sentiment'],
            marker_color=colors,
            name='Net Sentiment',
            hovertemplate='<b>%{x}</b><br>Net Sentiment: %{y}<extra></extra>',
            opacity=0.7
        ), row=1, col=1)

        # Add horizontal line at y=0
        fig.add_hline(
            y=0, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=1
        )

    if len(brent_data) > 0:
        fig.add_trace(go.Scatter(
            x=brent_data['Date'],
            y=brent_data['Close'],
            mode='lines',
            name='Brent Crude Oil Price',
            line=dict(color='#FFD700', width=3),
            hovertemplate='<b>%{x}</b><br>Brent Price: $%{y:.2f}<extra></extra>'
        ), row=2, col=1)

    # Update layout
    fig.update_layout(
        title=title,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        margin=dict(t=60, b=40, l=60, r=60)
    )

    # Style axes
    fig.update_xaxes(title_text="Date", gridcolor='rgba(255,255,255,0.1)', row=2, col=1)
    fig.update_yaxes(title_text="Net Sentiment", gridcolor='rgba(255,255,255,0.1)', row=1, col=1)
    fig.update_yaxes(title_text="Brent Price ($USD)", tickfont=dict(color="#FFD700"), gridcolor='rgba(255,215,0,0.1)', row=2, col=1)

    return fig

# Load data
with st.spinner('🔄 Connecting to MongoDB and loading data...'):
    df = load_data()

# Connection status
if len(df) > 0:
    st.markdown('<div class="connection-status connection-success">✅ Successfully connected to MongoDB</div>', 
                unsafe_allow_html=True)
else:
    st.markdown('<div class="connection-status connection-error">❌ No data available or connection failed</div>', 
                unsafe_allow_html=True)
    st.stop()

# Sidebar for controls
with st.sidebar:
    st.markdown('<h2 style="color: #FFD700;">⚙️ CONTROLS</h2>', unsafe_allow_html=True)
    
    # Add refresh button at the top of sidebar
    if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
        with st.spinner('🔄 Refreshing data from MongoDB...'):
            load_data.clear()
            load_brent_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Date range picker
    if len(df) > 0:
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        default_start = max(min_date, max_date - timedelta(days=90))
        
        st.markdown("**📅 Date Range**")
        start_date, end_date = st.date_input(
            "Select date range:",
            value=(default_start, max_date),
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed"
        )
        
        st.markdown("**🎯 Filters**")
        
        # Category filter
        categories = sorted(df['Category'].dropna().unique())
        selected_categories = st.multiselect(
            "Select categories:",
            categories,
            default=categories,
            label_visibility="collapsed"
        )
        
        filter_sentiments = st.checkbox(
            "Show only Bullish and Bearish sentiment", 
            value=True
        )
    else:
        st.markdown("No data available for filtering")
        start_date = end_date = datetime.now().date()
        selected_categories = []
        filter_sentiments = True

# Apply filtering
if len(df) > 0:
    # Date filter
    df_filtered = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
    
    # Category filter
    if selected_categories:
        df_filtered = df_filtered[df_filtered['Category'].isin(selected_categories)]
    
    # Sentiment filter
    if filter_sentiments:
        df_filtered = df_filtered[df_filtered['Sentiment'].isin(['bullish', 'bearish'])]
    
    # Create time-based datasets
    now = datetime.now()
    df_3d = df_filtered[df_filtered['Date'] >= now - timedelta(days=3)]
    df_7d = df_filtered[df_filtered['Date'] >= now - timedelta(days=7)]
    df_30d = df_filtered[df_filtered['Date'] >= now - timedelta(days=30)]

    # Load Brent crude oil data for the selected date range
    with st.spinner('📈 Loading Brent crude oil price data...'):
        brent_data = load_brent_data(start_date, end_date + timedelta(days=1))

    # Key metrics section
    st.markdown('<div class="section-header">📊 SENTIMENT OVERVIEW</div>', unsafe_allow_html=True)
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    datasets = [
        (df_filtered, "Selected Range", col1),
        (df_3d, "Last 3 Days", col2),
        (df_7d, "Last 7 Days", col3),
        (df_30d, "Last 30 Days", col4)
    ]
    
    for data, period, col in datasets:
        with col:
            # Chart
            fig = plotly_donut(data['Sentiment'], period)
            st.plotly_chart(fig, use_container_width=True)
            
            # Top words
            if len(data) > 0:
                top_words = get_top_phrases(data['Reasoning'], stop_words)
                if top_words:
                    for word, count in top_words:
                        st.markdown(f'<span class="word-item">{word} ({count})</span>', unsafe_allow_html=True)

    # Time series chart section with Brent overlay
    st.markdown('<div class="section-header">📈 NET SENTIMENT vs BRENT CRUDE OIL PRICE</div>', unsafe_allow_html=True)
    
    if len(df_filtered) > 0 or len(brent_data) > 0:
        combined_fig = create_net_sentiment_with_brent_chart(df_filtered, brent_data)
        st.plotly_chart(combined_fig, use_container_width=True)
        
        # Display current Brent price if available
        if len(brent_data) > 0:
            latest_price = brent_data.iloc[-1]['Close']
            latest_date = pd.to_datetime(brent_data.iloc[-1]['Date']).strftime('%Y-%m-%d')
            st.markdown(f'<div style="text-align: center; color: #FFD700; font-size: 1.1rem; margin: 1rem 0;">🛢️ Latest Brent Price: <strong>${latest_price:.2f}</strong> (as of {latest_date})</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align: center; color: #B0B0B0; padding: 2rem;">No data available for the selected filters to display trend chart.</div>', unsafe_allow_html=True)

    # News feed section
    st.markdown('<div class="section-header">📰 SENTIMENT ANALYSIS FEED</div>', unsafe_allow_html=True)
    
    if len(df_filtered) == 0:
        st.markdown('<div style="text-align: center; color: #B0B0B0; padding: 2rem;">No data available for the selected filters.</div>', unsafe_allow_html=True)
    else:
        # Sort by date descending
        display_df = df_filtered.sort_values('Date', ascending=False)
        
        for _, row in display_df.iterrows():
            sentiment_class = f"sentiment-{row['Sentiment']}" if row['Sentiment'] in ['bullish', 'bearish'] else 'sentiment-neutral'
            
            news_html = f'''
            <div class="news-item">
                <div class="news-header">
                    <div class="news-title">{row['Title']}</div>
                    <div class="news-meta">
                        <span class="category-badge">{row.get('Category', 'General')}</span>
                        <span class="sentiment-badge {sentiment_class}">{row['Sentiment'].upper()}</span>
                        <div class="news-date">📅 {row['Date'].strftime('%m/%d/%y')}</div>
            '''
            
            if pd.notna(row.get('Link', '')):
                news_html += f'<a href="{row["Link"]}" class="news-link" target="_blank">🔗 Read</a>'
            
            news_html += f'''
                    </div>
                </div>
                <div class="reasoning-text">
                    <span class="reasoning-label">💡 Analysis:</span>
                    {row.get('Reasoning', 'Analysis not available')}
                </div>
            </div>
            '''
            
            st.markdown(news_html, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #B0B0B0; padding: 1rem;">© 2024 Black Gold Analytics - Premium Market Intelligence</div>',
    unsafe_allow_html=True
)