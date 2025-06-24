import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Sentiment Analysis", layout="wide")
st.title("🛢️ Black Gold Analytics - Sentiment Analysis")

# Upload Excel file
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

if uploaded_file:
    # Read Excel data
    df = pd.read_excel(uploaded_file)
    

    # Convert 'Date' to pandas datetime if not already
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Slider returns datetime.date, so convert to datetime64 for filtering
    start_date, end_date = st.slider(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )

    # Convert dates for filtering
    mask = (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
    filtered_df = df.loc[mask]

    # Display filtered data
    st.subheader("Filtered Sentiment Data")
    st.dataframe(filtered_df[['Date', 'Title', 'Sentiment V2', 'Reasoning']])

    # Sentiment distribution chart
    st.subheader("Sentiment Distribution")
    sentiment_counts = filtered_df['Sentiment V2'].value_counts()

    fig, ax = plt.subplots()
    sentiment_counts.plot(kind='bar', color=['green', 'red', 'gray'], ax=ax)
    ax.set_ylabel("Count")
    ax.set_title("Sentiment Count")
    st.pyplot(fig)

else:
    st.info("Please upload your sentiment Excel file to get started.")
