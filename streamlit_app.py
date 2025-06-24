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

    # Ensure correct datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # Date slider to filter data
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    selected_date_range = st.slider("Select Date Range", min_value=min_date, max_value=max_date,
                                    value=(min_date, max_date), format="YYYY-MM-DD")

    # Filter data
    mask = (df['Date'] >= selected_date_range[0]) & (df['Date'] <= selected_date_range[1])
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
