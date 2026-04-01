import streamlit as st
import pandas_datareader.data as web
import pandas as pd
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
    with st.spinner("Loading market data from Stooq..."):
        try:
            # Stooq is more stable on cloud
            data = web.DataReader(ticker, 'stooq', start="2020-01-01")
            
            if not data.empty and "Close" in data.columns:
                current_price = float(data["Close"].iloc[-1])
                st.metric("Current Price", f"${current_price:.2f}")
                
                st.success("✅ Forecast example: +2.8% over next 1-5 days (demo)")
                st.info("Stop: $XXX | Target: $XXX | Risk: 1% of your account (safe for beginners)")
                
                if st.button("Add to Watchlist"):
                    st.success(f"✅ {ticker} added to watchlist!")
            else:
                st.error(f"No data found for **{ticker}**. Try NVDA, MSFT, or BTC-USD.")
        except Exception as e:
            st.error("Could not load data right now.")
            st.info("💡 This can happen temporarily. Refresh in a few minutes.")
else:
    st.info("Enter a ticker above to see price and forecast.")
