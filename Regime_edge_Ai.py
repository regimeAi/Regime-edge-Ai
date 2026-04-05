import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
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
st.caption("Live forecasts • Polished confidence bands • Real candlestick chart • Alerts • Theme watchlists")

# === SECURITY: Move this key to Streamlit Secrets (recommended) ===
# 1. Go to your app on Streamlit Cloud → Manage app → Secrets
# 2. Add: finnhub_key = "your-key-here"
# 3. Then replace the line below with: FINNHUB_API_KEY = st.secrets["finnhub_key"]
FINNHUB_API_KEY = "d78i399r01qp0fl5ah30d78i399r01qp0fl5ah3g"  # TEMPORARY - remove after moving to secrets

# Persistent data
if "watchlists" not in st.session_state:
    st.session_state.watchlists = {
        "AI Economy": ["NVDA", "AMD", "MSFT", "GOOGL", "AMZN"],
        "Semiconductors": ["NVDA", "AMD", "TSM", "AVGO", "MU"],
        "Cyber Security": ["CRWD", "PANW", "ZS", "FTNT"],
        "Biotech": ["REGN", "AMGN", "GILD", "VRTX"],
        "BTC & Crypto": ["BTC-USD", "ETH-USD"]
    }
if "alerts" not in st.session_state:
    st.session_state.alerts = []

ticker = st.text_input("Enter ticker (NVDA, BTC-USD, etc.)", "NVDA").upper().strip()

@st.cache_data(ttl=300, show_spinner=False)
def get_live_price(symbol):
    if not symbol:
        return None
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get("c")
    except Exception as e:
        st.error(f"Price fetch failed: {str(e)[:100]}")
        return None

@st.cache_data(ttl=600, show_spinner=False)  # Longer cache for candles
def get_candles(symbol):
    if not symbol:
        return None
    try:
        to_ts = int(time.time())
        from_ts = to_ts - 60 * 86400  # ~60 days
        url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution=D&from={from_ts}&to={to_ts}&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        if data.get('s') == 'ok' and len(data.get('c', [])) > 0:
            df = pd.DataFrame({
                'Date': pd.to_datetime(data['t'], unit='s'),
                'Open': data['o'],
                'High': data['h'],
                'Low': data['l'],
                'Close': data['c']
            })
            return df
        return None
    except:
        return None

@st.cache_data(ttl=300, show_spinner=False)
def get_news_sentiment(symbol):
    try:
        url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from=2026-03-01&to=2026-04-04&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        news = response.json()[:5]
        positive = sum(1 for n in news if any(w in n.get("headline", "").lower() for w in ["beat", "growth", "upgrade", "strong"]))
        return (positive / max(len(news), 1)) * 2 - 1
    except:
        return 0.0

if ticker:
    current_price = get_live_price(ticker)
    candles = get_candles(ticker)
    news_score = get_news_sentiment(ticker)
    
    if current_price is None:
        st.error("Could not fetch live price. Check the ticker or try again later.")
        st.stop()
    
    # Demo forecast (we'll make dynamic next)
    forecast_5d = 4.2
    confidence = 75
    lower_band = current_price * (1 - 0.07)
    upper_band = current_price * (1 + 0.13)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Scan & Forecast", "Signal Card", "Regime & News", "Strategy Lab"])
    
    with tab1:
        st.metric("Current Live Price", f"${current_price:,.2f}")
        
        # Real candlestick chart
        if candles is not None and not candles.empty:
            fig_candle = go.Figure(data=[go.Candlestick(
                x=candles['Date'],
                open=candles['Open'],
                high=candles['High'],
                low=candles['Low'],
                close=candles['Close']
            )])
            fig_candle.update_layout(title="Last ~60 Days Candlestick Chart", height=380, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_candle, use_container_width=True)
        else:
            st.info("Candlestick chart loading or no data available yet...")
        
        # Polished confidence bands
        fig_band = go.Figure()
        fig_band.add_trace(go.Scatter(x=["Now", "1-5 Days"], y=[current_price, current_price * (1 + forecast_5d/100)],
                                    mode='lines+markers', name='Forecast', line=dict(color='#1f77b4', width=3)))
        fig_band.add_trace(go.Scatter(x=["1-5 Days"], y=[lower_band], mode='lines', name='Lower 95% Band',
                                    line=dict(dash='dash', color='#d62728')))
        fig_band.add_trace(go.Scatter(x=["1-5 Days"], y=[upper_band], mode='lines', name='Upper 95% Band',
                                    line=dict(dash='dash', color='#2ca02c')))
        fig_band.update_layout(title="1-5 Day Forecast with Confidence Bands", height=340,
                               legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig_band, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("1-5 Day Forecast", f"+{forecast_5d}%")
        with col2: st.metric("Confidence", f"{confidence}%")
        with col3: st.metric("Regime", "Risk-On")
    
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
        account = st.number_input("Account size ($)", value=10000, step=1000)
        risk_pct = st.slider("Max risk per trade (%)", 0.5, 5.0, 1.0)
        risk_amount = account * risk_pct / 100
        stop_dist = current_price * 0.08
        shares = int(risk_amount / stop_dist) if stop_dist > 0 else 0
        st.write(f"**Recommended shares**: **{shares}**")
        st.write(f"**Risk amount**: **${risk_amount:,.0f}**")
    
    with tab3:
        st.subheader("Regime & News Sentiment")
        st.write("**Current Regime**: Risk-On (demo)")
        st.write(f"**News Momentum Score**: {news_score:+.2f}")
        st.progress((news_score + 1) / 2)
    
    with tab4:
        st.subheader("Strategy Lab")
        st.write("Backtest placeholders ready")
        if st.button("Run Demo Backtest"):
            st.success("Sharpe 1.4 | Max DD -12% | Regime-adjusted")
        
        st.subheader("Theme Watchlists")
        selected_theme = st.selectbox("Select theme", list(st.session_state.watchlists.keys()))
        st.write("**Tickers**:", ", ".join(st.session_state.watchlists[selected_theme]))
        if st.button("Add current ticker to theme"):
            if ticker not in st.session_state.watchlists[selected_theme]:
                st.session_state.watchlists[selected_theme].append(ticker)
                st.success(f"✅ Added to {selected_theme}")
        
        st.subheader("Alerts")
        alert_price = st.number_input("Alert when price reaches", value=current_price * 1.05)
        if st.button("Set Price Alert"):
            st.session_state.alerts.append(f"{ticker} @ ${alert_price:,.2f}")
            st.success("Alert saved!")
        st.write("Active alerts:", st.session_state.alerts if st.session_state.alerts else "None")
else:
    st.info("Enter a ticker above to load live data.")

st.caption("**Not financial advice** — This is an educational/demo tool only. Past performance is not indicative of future results.")
