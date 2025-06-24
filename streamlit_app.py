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

    # Validate and clean date column
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])  # Drop rows where date conversion failed

    # Filter using date slider
    min_date = df['Date'].min()
    max_date = df['Date'].max()

    start_date, end_date = st.slider(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )

    # Apply filter
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    filtered_df = df.loc[mask]

    # Display data
    st.subheader("Filtered Sentiment Data")
    st.dataframe(filtered_df[['Date', 'Title', 'Sentiment V2', 'Reasoning']])

    # Plot sentiment distribution
    st.subheader("Sentiment Distribution")
    sentiment_counts = filtered_df['Sentiment V2'].value_counts()

    fig, ax = plt.subplots()
    sentiment_counts.plot(kind='bar', color=['green', 'red', 'gray'], ax=ax)
    ax.set_ylabel("Count")
    ax.set_title("Sentiment Count")
    st.pyplot(fig)

else:
    st.error(f"File '{file_path}' not found in the directory.")
