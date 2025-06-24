import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import plotly.graph_objects as go
import re
from collections import Counter

st.set_page_config(page_title="Sentiment Analysis", layout="wide")
st.title("🛢️ Black Gold Analytics - Sentiment Analysis")

# Define file path
file_path = "sentiment_v2_with_reasoning.xlsx"

# Define stop words to exclude from top words
stop_words = set([
    'the', 'and', 'is', 'to', 'in', 'of', 'for', 'on', 'with', 'at', 'by', 'an',
    'be', 'this', 'that', 'from', 'as', 'are', 'it', 'was', 'or', 'which',
    # Add more words to exclude here
])

def get_top_words(text_series, stop_words, top_n=5):
    combined_text = " ".join(text_series.dropna().astype(str)).lower()
    words = re.findall(r'\b[a-z]+\b', combined_text)
    filtered_words = [word for word in words if word not in stop_words]
    word_counts = Counter(filtered_words)
    return word_counts.most_common(top_n)

if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    df['Date'] = pd.to_datetime(df['Date'])

    # Date range picker
    min_date = df['Date'].min()
    max_date = df['Date'].max()

    start_date, end_date = st.date_input(
        "Select date range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    # Checkbox to exclude non Bullish/Bearish rows
    filter_sentiments = st.checkbox(
        "Show only Bullish and Bearish rows", value=True
    )

    # Apply filtering if checked
    if filter_sentiments:
        df = df[df['Sentiment V2'].isin(['bullish', 'bearish'])]

    def plotly_donut(sentiments, title):
        counts = sentiments.value_counts()
        labels = counts.index.tolist()
        values = counts.tolist()

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            textinfo='label+percent',
            hoverinfo='label+value'
        )])
        fig.update_layout(title_text=title, margin=dict(t=40, b=0, l=0, r=0))
        return fig

    df_selected = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
    df_3d = df[df['Date'] >= datetime.now() - timedelta(days=3)]
    df_7d = df[df['Date'] >= datetime.now() - timedelta(days=7)]
    df_30d = df[df['Date'] >= datetime.now() - timedelta(days=30)]

    st.subheader("📊 Sentiment Distribution")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.plotly_chart(plotly_donut(df_selected['Sentiment V2'], "Selected Range"), use_container_width=True)
        top_words = get_top_words(df_selected['Reasoning'], stop_words)
        if top_words:
            st.markdown("**Top 5 words:**")
            for word, count in top_words:
                st.markdown(f"- {word} ({count})")
        else:
            st.markdown("No words found")

    with col2:
        st.plotly_chart(plotly_donut(df_3d['Sentiment V2'], "Last 3 Days"), use_container_width=True)
        top_words = get_top_words(df_3d['Reasoning'], stop_words)
        if top_words:
            st.markdown("**Top 5 words:**")
            for word, count in top_words:
                st.markdown(f"- {word} ({count})")
        else:
            st.markdown("No words found")

    with col3:
        st.plotly_chart(plotly_donut(df_7d['Sentiment V2'], "Last 7 Days"), use_container_width=True)
        top_words = get_top_words(df_7d['Reasoning'], stop_words)
        if top_words:
            st.markdown("**Top 5 words:**")
            for word, count in top_words:
                st.markdown(f"- {word} ({count})")
        else:
            st.markdown("No words found")

    with col4:
        st.plotly_chart(plotly_donut(df_30d['Sentiment V2'], "Last 30 Days"), use_container_width=True)
        top_words = get_top_words(df_30d['Reasoning'], stop_words)
        if top_words:
            st.markdown("**Top 5 words:**")
            for word, count in top_words:
                st.markdown(f"- {word} ({count})")
        else:
            st.markdown("No words found")

    st.markdown("---")

    filtered_df = df_selected[['Date', 'Title', 'Sentiment V2', 'Link', 'Reasoning']]

    col1, col2, col3 = st.columns([3, 1, 4])
    with col1:
        st.markdown("### 📰 Title & Link")
    with col2:
        st.markdown("### 📊 Sentiment")
    with col3:
        st.markdown("### 🧠 Reasoning")

    st.markdown("---")

    for _, row in filtered_df.iterrows():
        col1, col2, col3 = st.columns([3, 1, 4])
        with col1:
            st.markdown(f"**{row['Title']}**")
            st.markdown(f"<small>{row['Date'].strftime('%b %d, %Y')}</small>", unsafe_allow_html=True)
            if pd.notna(row['Link']):
                st.markdown(f"[🔗 Link]({row['Link']})")
        with col2:
            st.markdown(f"{row['Sentiment V2']}")
        with col3:
            st.markdown(f"{row['Reasoning']}")
        st.markdown("---")

else:
    st.error(f"File not found: {file_path}")
