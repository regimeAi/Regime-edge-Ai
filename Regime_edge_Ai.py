
import streamlit as st
import requests
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

# Your Finnhub API key (already inserted)
FINNHUB_API_KEY = "d78i399r01qp0fl5ah30d78i399r01qp0fl5ah3g"

# Tabs for navigation
tab1, tab2, tab3 = st.tabs(["Scan & Forecast", "Signal Card", "My Watchlist"])

if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["NVDA", "AMD", "MSFT", "BTC-USD"]

ticker = st.text_input("Enter ticker (NVDA, BTC-USD, etc.)", "NVDA").upper().strip()

@st.cache_data(ttl=60)  # Cache for 60 seconds to stay under free tier limits
def get_live_price(symbol):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            price = data.get("c")  # current price
            if price and price > 0:
                return price
        return None
    except:
        return None

if ticker:
    with st.spinner("Fetching live price from Finnhub..."):
        current_price = get_live_price(ticker)
        
        if current_price:
            st.metric("Current Live Price", f"${current_price:,.2f}")
            
            # Demo forecasts (replace with real models later)
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
                
                # Clean position sizing
                account = st.number_input("Account size ($)", value=10000, step=1000)
                risk_pct = st.slider("Max risk per trade (%)", 0.5, 5.0, 1.0)
                risk_amount = account * risk_pct / 100
                stop_dist = current_price * 0.08
                shares = int(risk_amount / stop_dist) if stop_dist > 0 else 0
                st.write(f"**Recommended shares**: **{shares}**")
                st.write(f"**Risk amount**: **${risk_amount:,.0f}**")
        else:
            st.error("Could not fetch price. Make sure the ticker is valid (try NVDA or BTC-USD).")
else:
    st.info("Enter a ticker above to load live data.")

with tab3:
    st.subheader("My Watchlist")
    for t in st.session_state.watchlist:
        st.write(f"• {t}")

st.caption("Live prices via Finnhub • Next: regime detection + news sentiment • Not financial advice")
