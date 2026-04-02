import streamlit as st
import yfinance as yf
import time
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="RegimeEdge AI",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("RegimeEdge AI")
st.caption("Stock forecasts • iPhone friendly • Beginner safe")

ticker = st.text_input("Type a ticker (example: NVDA or BTC-USD)", "NVDA").upper().strip()

if ticker:
    with st.spinner("Loading market data... (may take a moment on cloud)"):
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                data = yf.download(ticker, period="6mo", interval="1d", progress=False, timeout=15)
                
                if not data.empty and "Close" in data.columns:
                    current_price = float(data["Close"].iloc[-1])
                    st.metric("Current Price", f"${current_price:.2f}")
                    
                    st.success("✅ Forecast example: +2.8% over next 1-5 days (demo)")
                    st.info("Stop: $XXX | Target: $XXX | Risk: 1% of your account (safe for beginners)")
                    
                    if st.button("Add to Watchlist"):
                        st.success(f"✅ {ticker} added to watchlist!")
                    break  # Success, exit retry loop
                else:
                    raise ValueError("Empty data returned")
            except Exception as e:
                if attempt < max_retries:
                    time.sleep(3)  # short wait before retry
                    continue
                else:
                    st.error(f"Could not load data for **{ticker}** right now.")
                    st.info("💡 Yahoo Finance sometimes rate-limits free cloud apps. Wait 15–60 minutes and refresh the page.")
else:
    st.info("Enter a ticker above to see price and forecast.")
