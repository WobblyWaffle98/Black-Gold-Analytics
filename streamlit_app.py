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

    # Ensure 'Date' column is in datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # Set default start and end dates for the picker
    min_date = df['Date'].min()
    max_date = df['Date'].max()

    # Date range picker
    start_date, end_date = st.date_input(
        "Select date range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Filter DataFrame based on selected date range
    mask = (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
    filtered_df = df.loc[mask]

    st.write(filtered_df)
else:
    st.error(f"File not found: {file_path}")
