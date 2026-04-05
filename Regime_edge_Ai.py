import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import time
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="RegimeEdge AI", page_icon="📈", layout="centered", initial_sidebar_state="collapsed")

st.title("RegimeEdge AI")
st.caption("Live forecasts • Real candlestick • Polished bands • Theme watchlists")

# === SECURITY NOTE ===
# Move your API key to Streamlit secrets in production (st.secrets["finnhub_key"])
FINNHUB_API_KEY = "d78i399r01qp0fl5ah30d78i399r01qp0fl5ah3g"   # ← TEMPORARY — change later!

# Persistent data
if "watchlists" not in st.session_state:
    st.session_state.watchlists = { ... }  # keep your existing watchlists dict

ticker = st.text_input("Enter ticker", "NVDA").upper().strip()

@st.cache_data(ttl=300, show_spinner=False)
def get_live_price(symbol):
    if not symbol: return None
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json().get("c")
    except:
        return None

# ... (keep get_candles and get_news_sentiment but add better error handling)

# Then in the main if ticker block:
current_price = get_live_price(ticker)

if current_price is None:
    st.error("Could not fetch price. Check ticker or try again later.")
    st.stop()

# Calculate a simple regime from price (you can improve this later)
regime = "Risk-On" if current_price > 100 else "High-Vol"   # placeholder logic

# Rest of your tabs with the polished confidence bands and candlestick remain similar.
