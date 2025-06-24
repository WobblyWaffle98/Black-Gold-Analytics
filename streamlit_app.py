import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Sentiment Analysis", layout="wide")
st.title("🛢️ Black Gold Analytics - Sentiment Analysis")

# Define file path
file_path = "sentiment_v2_with_reasoning.xlsx"

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

    # Function to create Plotly donut chart
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

    # Prepare filtered datasets
    df_selected = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
    df_1d = df[df['Date'] >= datetime.now() - timedelta(days=1)]
    df_7d = df[df['Date'] >= datetime.now() - timedelta(days=7)]
    df_30d = df[df['Date'] >= datetime.now() - timedelta(days=30)]

    st.subheader("📊 Sentiment Distribution")

    col1, col2, col3, col4= st.columns(4)
    with col1:
        st.plotly_chart(plotly_donut(df_selected['Sentiment V2'], "Selected Range"), use_container_width=True)
    with col2:
        st.plotly_chart(plotly_donut(df_1d['Sentiment V2'], "Last 1 Days"), use_container_width=True)
    with col3:
        st.plotly_chart(plotly_donut(df_7d['Sentiment V2'], "Last 7 Days"), use_container_width=True)
    with col4:
        st.plotly_chart(plotly_donut(df_30d['Sentiment V2'], "Last 30 Days"), use_container_width=True)

    st.markdown("---")

    # Filtered table data
    filtered_df = df_selected[['Date', 'Title', 'Sentiment V2', 'Link', 'Reasoning']]

    # Table headers
    col1, col2, col3 = st.columns([3, 1, 4])
    with col1:
        st.markdown("### 📰 Title & Link")
    with col2:
        st.markdown("### 📊 Sentiment")
    with col3:
        st.markdown("### 🧠 Reasoning")

    st.markdown("---")

    # Display entries
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
