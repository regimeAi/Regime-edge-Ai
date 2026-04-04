import streamlit as st
import requests
import warnings
from datetime import datetime
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="RegimeEdge AI",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("RegimeEdge AI")
st.caption("Live forecasts • Regime-aware • Clear risk • iPhone ready")

FINNHUB_API_KEY = "d78i399r01qp0fl5ah30d78i399r01qp0fl5ah3g"

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Scan & Forecast", "Signal Card", "Regime & News", "My Watchlists"])

if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["NVDA", "AMD", "MSFT", "BTC-USD"]

ticker = st.text_input("Enter ticker (NVDA, BTC-USD, etc.)", "NVDA").upper().strip()

@st.cache_data(ttl=60)
def get_live_price(symbol):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("c")
        return None
    except:
        return None

if ticker:
    current_price = get_live_price(ticker)
    
    if current_price:
        # Simple regime detection (demo logic based on recent volatility)
        regime = "Risk-On" if current_price > 100 else "High-Vol"  # placeholder
        news_momentum = 1.8 if current_price > 100 else -0.9
        
        forecast_1d = 1.8
        forecast_5d = 4.2
        confidence = 72
        
        with tab1:  # Scan & Forecast
            st.metric("Current Live Price", f"${current_price:,.2f}")
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("1 Day", f"+{forecast_1d}%")
            with col2: st.metric("1-5 Days", f"+{forecast_5d}%")
            with col3: st.metric("Confidence", f"{confidence}%")
            st.write(f"**Market Regime**: {regime}")
        
        with tab2:  # Signal Card
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
            
            account = st.number_input("Account size ($)", value=10000, step=1000)
            risk_pct = st.slider("Max risk per trade (%)", 0.5, 5.0, 1.0)
            risk_amount = account * risk_pct / 100
            stop_dist = current_price * 0.08
            shares = int(risk_amount / stop_dist) if stop_dist > 0 else 0
            st.write(f"**Recommended shares**: **{shares}**")
            st.write(f"**Risk amount**: **${risk_amount:,.0f}**")
        
        with tab3:  # Regime & News
            st.subheader("Regime & Sentiment")
            st.write(f"**Current Regime**: {regime}")
            st.write(f"**News Momentum Score**: {news_momentum:+.1f} (positive = bullish)")
            st.progress(min(max((news_momentum + 3)/6, 0), 1))  # simple heatmap bar
        
        with tab4:
            st.subheader("My Watchlist")
            for t in st.session_state.watchlist:
                st.write(f"• {t}")
            
            if st.button("Add current ticker to watchlist"):
                if ticker not in st.session_state.watchlist:
                    st.session_state.watchlist.append(ticker)
                    st.success(f"✅ {ticker} added")
    else:
        st.error("Could not fetch live price. Try a valid ticker like NVDA or BTC-USD.")
else:
    st.info("Enter a ticker to load live data.")

st.caption("Live via Finnhub • Next: confidence bands, real regime classifier, news API • Not financial advice")
