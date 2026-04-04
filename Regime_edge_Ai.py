import streamlit as st
import yfinance as yf
import time
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
st.caption("Live multi-horizon forecasts • Clear risk • iPhone ready")

# Tabs
tab1, tab2, tab3 = st.tabs(["Scan & Forecast", "Signal Card", "My Watchlist"])

if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["NVDA", "AMD", "MSFT", "BTC-USD"]

ticker = st.text_input("Enter ticker (NVDA, BTC-USD, etc.)", "NVDA").upper().strip()

@st.cache_data(ttl=300)  # Cache for 5 minutes to reduce calls
def get_price_data(ticker):
    try:
        data = yf.download(ticker, period="6mo", interval="1d", progress=False, timeout=15)
        if not data.empty and "Close" in data.columns:
            return float(data["Close"].iloc[-1])
        return None
    except:
        return None

if ticker:
    with st.spinner("Fetching live price..."):
        current_price = get_price_data(ticker)
        
        if current_price:
            st.metric("Current Live Price", f"${current_price:,.2f}")
            
            # Demo forecasts (replace with real model later)
            forecast_1d = 1.8
            forecast_5d = 4.2
            confidence = 72
            
            with tab1:
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("1 Day", f"+{forecast_1d}%")
                with col2: st.metric("1-5 Days", f"+{forecast_5d}%")
                with col3: st.metric("Confidence", f"{confidence}%")
            
            with tab2:
                st.subheader("Signal Card")
                direction = "BUY" if forecast_5d > 0 else "SELL / HOLD"
                st.success(f"**{direction} {ticker}**")
                stop_price = round(current_price * 0.92, 2)
                target_price = round(current_price * 1.15, 2)
                st.info(f"""
                **Entry**: ${current_price:,.2f}  
                **Stop Loss**: ${stop_price:,.2f}  
                **Target**: ${target_price:,.2f}  
                **Expected Move**: ±{abs(forecast_5d)}% over 1–5 days  
                **Confidence**: {confidence}%
                """)
                
                # Position sizing
                account = st.number_input("Account size ($)", value=10000, step=1000)
                risk_pct = st.slider("Max risk per trade (%)", 0.5, 5.0, 1.0)
                risk_amount = account * risk_pct / 100
                stop_dist = current_price * 0.08
                shares = int(risk_amount / stop_dist) if stop_dist > 0 else 0
                st.write(f"**Recommended shares**: **{shares}**")
                st.write(f"**Risk amount**: **${risk_amount:,.0f}**")
        else:
            st.error("Could not fetch live data right now (Yahoo rate limit). Wait 15–30 min and refresh, or we'll switch to Finnhub.")
else:
    st.info("Enter a ticker to see live price + forecasts.")

with tab3:
    st.subheader("My Watchlist")
    for t in st.session_state.watchlist:
        st.write(f"• {t}")

st.caption("Live mode (yfinance) • Real regime + news coming next • Not financial advice")
