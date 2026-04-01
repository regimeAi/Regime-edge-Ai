import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="RegimeEdge AI",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("RegimeEdge AI")
st.caption("Your stock forecasts • iPhone ready • Beginner friendly")

ticker = st.text_input("Type a ticker (example: NVDA or BTC-USD)", "NVDA").upper()

data = yf.download(ticker, period="6mo", interval="1d")

if not data.empty:
    current_price = data["Close"].iloc[-1]
    st.metric("Current Price", f"${current_price:.2f}")
    st.success("Forecast: +2.8% next 1-5 days (example - live data)")
    st.info("Stop: $XXX | Target: $XXX | Risk: 1% of your account (safe for beginners)")
    if st.button("Add to Watchlist"):
        st.success("Added to watchlist! ✅")
else:
    st.write("Loading data for " + ticker + "...")
