import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

st.set_page_config(page_title="Sentiment Analysis", layout="wide")
st.title("🛢️ Black Gold Analytics - Sentiment Analysis")

# Define the file path (same directory)
file_path = "sentiment_v2_with_reasoning.xlsx"

# Check if file exists
if os.path.exists(file_path):
    # Read Excel data
    df = pd.read_excel(file_path)

    # Ensure 'Date' is datetime
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

    # Filter by date
    mask = (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
    filtered_df = df.loc[mask]

    # Show only desired columns
    display_df = filtered_df[['Title', 'Sentiment V2', 'Link', 'Reasoning']]

    # Display each entry professionally
    for _, row in display_df.iterrows():
        st.subheader(row['Title'])
        st.markdown(f"**Sentiment:** {row['Sentiment V2']}")
        st.markdown(f"**Reasoning:** {row['Reasoning']}")
        if pd.notna(row['Link']):
            st.markdown(f"[Read more]({row['Link']})")
        st.markdown("---")
else:
    st.error(f"File not found: {file_path}")
