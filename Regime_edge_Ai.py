import streamlit as st
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
st.success("✅ App is now running stably! (Demo mode - real data coming soon)")

ticker = st.text_input("Type a ticker (example: NVDA or BTC-USD)", "NVDA").upper().strip()

if ticker:
    # Demo data - no external calls, no rate limits
    demo_prices = {
        "NVDA": 142.50,
        "AMD": 118.75,
        "MSFT": 428.30,
        "GOOGL": 168.40,
        "BTC-USD": 68250.00,
        "TSLA": 248.90
    }
    
    price = demo_prices.get(ticker, 125.67)  # default demo price
    
    st.metric("Current Price (Demo)", f"${price:,.2f}")
    
    st.success("✅ Forecast: +2.8% over next 1-5 days (demo)")
    st.info("Stop: $XXX | Target: $XXX | Risk: 1% of your account (safe for beginners)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add to Watchlist"):
            st.success(f"✅ {ticker} added!")
    with col2:
        if st.button("Show Signal Card"):
            st.info("BUY Signal • Confidence 75% • Poker-style edge: +EV like good pot odds")
else:
    st.info("Enter a ticker above to see demo forecast and risk tools.")

# Your future full features placeholder
st.subheader("Your Full RegimeEdge Features (Coming Next)")
st.write("- Multi-horizon forecasts with confidence bands")
st.write("- Explainable buy/sell signals")
st.write("- Poker-style position sizing & risk rules")
st.write("- Custom watchlists (AI, semis, bio, etc.)")
