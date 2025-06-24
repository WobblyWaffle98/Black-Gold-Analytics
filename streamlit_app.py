import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Sentiment Analysis", layout="wide")
st.title("🛢️ Black Gold Analytics - Sentiment Analysis")

# Define file path
file_path = "sentiment_v2_with_reasoning.xlsx"

# Load data
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

    # Filter data
    mask = (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
    filtered_df = df.loc[mask][['Date', 'Title', 'Sentiment V2', 'Link', 'Reasoning']]

    # Header row
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
