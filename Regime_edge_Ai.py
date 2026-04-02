import streamlit as st
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="RegimeEdge AI",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("RegimeEdge AI")
st.caption("Multi-horizon forecasts • Risk management • iPhone ready")

# Persistent watchlist
if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["NVDA", "AMD", "MSFT", "BTC-USD"]

ticker = st.text_input("Enter ticker (NVDA, BTC-USD, etc.)", "NVDA").upper().strip()

if ticker:
    # Demo data
    demo = {
        "NVDA": {"price": 142.50, "forecast_1d": 2.1, "forecast_5d": 4.8, "confidence": 78},
        "AMD": {"price": 118.75, "forecast_1d": 1.5, "forecast_5d": 3.9, "confidence": 65},
        "MSFT": {"price": 428.30, "forecast_1d": 1.2, "forecast_5d": 2.8, "confidence": 82},
        "BTC-USD": {"price": 68250.00, "forecast_1d": -2.3, "forecast_5d": 5.2, "confidence": 62},
    }
    
    info = demo.get(ticker, {"price": 125.67, "forecast_1d": 2.0, "forecast_5d": 4.5, "confidence": 70})
    
    st.metric("Current Price (Demo)", f"${info['price']:,.2f}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("1 Day Forecast", f"+{info['forecast_1d']}%")
    with col2:
        st.metric("1-5 Day Forecast", f"+{info['forecast_5d']}%")
    with col3:
        st.metric("Confidence", f"{info['confidence']}%")
    
    # Clean Signal Card
    st.subheader("Signal Card")
    direction = "BUY" if info['forecast_5d'] > 0 else "SELL / HOLD"
    st.success(f"**{direction} {ticker}**")
    
    stop_price = round(info['price'] * 0.92, 2)
    target_price = round(info['price'] * 1.15, 2)
    
    st.info(f"""
    **Entry**: ${info['price']:,.2f}  
    **Stop Loss**: ${stop_price:,.2f}  
    **Target**: ${target_price:,.2f}  
    **Expected Move**: ±{abs(info['forecast_5d'])}% over 1–5 days
    **Confidence**: {info['confidence']}%
    """)
    
    # Clean position sizing
    st.subheader("Position Sizing")
    account_size = st.number_input("Account size ($)", value=10000, step=1000)
    risk_percent = st.slider("Maximum risk per trade (%)", 0.5, 5.0, 1.0)
    
    risk_amount = account_size * (risk_percent / 100)
    stop_distance = info['price'] * 0.08  # 8% stop distance
    
    shares = int(risk_amount / stop_distance) if stop_distance > 0 else 0
    
    st.write(f"**Recommended shares**: **{shares}**")
    st.write(f"Risk amount: **${risk_amount:,.0f}** ({risk_percent}% of account)")
    st.caption("This keeps risk controlled per trade.")

    # Watchlist buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add to Watchlist"):
            if ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(ticker)
                st.success(f"✅ {ticker} added")
    with col2:
        if st.button("Clear Watchlist"):
            st.session_state.watchlist = []
            st.success("Watchlist cleared")

# Watchlist display
st.subheader("My Watchlist")
if st.session_state.watchlist:
    for t in st.session_state.watchlist:
        st.write(f"• {t}")
else:
    st.write("Watchlist is empty")

st.caption("Demo mode • Real data, regime detection, and news sentiment coming next • Not financial advice")
