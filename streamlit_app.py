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

    st.write(df)