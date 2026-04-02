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
st.caption("Multi-horizon forecasts • Clear risk • iPhone ready")

# Tabs for clean navigation
tab1, tab2, tab3 = st.tabs(["Scan & Forecast", "Signal Card", "Strategy Lab"])

# Persistent watchlist
if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["NVDA", "AMD", "MSFT", "BTC-USD"]

ticker = st.text_input("Enter ticker", "NVDA").upper().strip()

# Demo data with regime
demo = {
    "NVDA": {"price": 142.50, "1d": 2.1, "5d": 4.8, "conf": 78, "regime": "Risk-On"},
    "AMD": {"price": 118.75, "1d": 1.5, "5d": 3.9, "conf": 65, "regime": "High-Vol"},
    "MSFT": {"price": 428.30, "1d": 1.2, "5d": 2.8, "conf": 82, "regime": "Risk-On"},
    "BTC-USD": {"price": 68250.00, "1d": -2.3, "5d": 5.2, "conf": 62, "regime": "High-Vol"},
}

info = demo.get(ticker, {"price": 125.67, "1d": 2.0, "5d": 4.5, "conf": 70, "regime": "Risk-On"})

with tab1:  # Scan & Forecast
    st.metric("Current Price (Demo)", f"${info['price']:,.2f}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("1 Day", f"+{info['1d']}%")
    with col2:
        st.metric("1-5 Days", f"+{info['5d']}%")
    with col3:
        st.metric("Confidence", f"{info['conf']}%")
    
    st.write(f"**Market Regime**: {info['regime']}")
    
    # Simple news sentiment
    sentiment = 1.8 if info['5d'] > 0 else -0.9
    st.write(f"**News Momentum**: {sentiment:+.1f} (positive = bullish)")
    
    if st.button("Add to Watchlist"):
        if ticker not in st.session_state.watchlist:
            st.session_state.watchlist.append(ticker)
            st.success(f"✅ {ticker} added")

with tab2:  # Signal Card
    st.subheader("Signal Card")
    direction = "BUY" if info['5d'] > 0 else "SELL / HOLD"
    st.success(f"**{direction} {ticker}**")
    
    stop_price = round(info['price'] * 0.92, 2)
    target_price = round(info['price'] * 1.15, 2)
    
    st.info(f"""
    **Entry**: ${info['price']:,.2f}  
    **Stop Loss**: ${stop_price:,.2f} (8% below entry)  
    **Target**: ${target_price:,.2f} (15% upside)  
    **Expected Move**: ±{abs(info['5d'])}% over 1–5 days  
    **Confidence**: {info['conf']}%
    """)
    
    # Position sizing
    st.subheader("Position Sizing")
    account_size = st.number_input("Account size ($)", value=10000, step=1000)
    risk_percent = st.slider("Max risk per trade (%)", 0.5, 5.0, 1.0)
    
    risk_amount = account_size * (risk_percent / 100)
    stop_distance = info['price'] * 0.08
    shares = int(risk_amount / stop_distance) if stop_distance > 0 else 0
    
    st.write(f"**Recommended shares**: **{shares}**")
    st.write(f"**Risk amount**: **${risk_amount:,.0f}** ({risk_percent}% of account)")

with tab3:  # Strategy Lab (placeholder)
    st.subheader("Strategy Lab")
    st.write("Build or tune strategies here (coming soon)")
    st.write("- Trend following")
    st.write("- Post-earnings drift")
    st.write("- Volatility compression")
    st.write("Backtest with regime filters • Risk overlays")

# Watchlist (visible on all tabs)
st.subheader("My Watchlist")
if st.session_state.watchlist:
    for t in st.session_state.watchlist:
        st.write(f"• {t}")
else:
    st.write("Empty")

st.caption("Demo mode • Real data + full news scoring + backtesting coming next • Not financial advice")
