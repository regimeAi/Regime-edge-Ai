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

FINNHUB_API_KEY = "d78i399r01qp0fl5ah30d78i399r01qp0fl5ah3g"

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

@st.cache_data(ttl=60)
def get_live_price(symbol):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get("c")
        return None
    except:
        return None

@st.cache_data(ttl=300)
def get_candles(symbol):
    try:
        to_ts = int(time.time())
        from_ts = to_ts - 60 * 86400  # last 60 days
        url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution=D&from={from_ts}&to={to_ts}&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('s') == 'ok':
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

@st.cache_data(ttl=300)
def get_news_sentiment(symbol):
    try:
        url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from=2026-03-01&to=2026-04-04&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            news = response.json()[:5]
            positive = sum(1 for n in news if any(w in n.get("headline", "").lower() for w in ["beat", "growth", "upgrade", "strong"]))
            return (positive / max(len(news), 1)) * 2 - 1
        return 0.0
    except:
        return 0.0

if ticker:
    current_price = get_live_price(ticker)
    candles = get_candles(ticker)
    news_score = get_news_sentiment(ticker)
    
    if current_price:
        # Demo forecast (will make dynamic next)
        forecast_5d = 4.2
        confidence = 75
        lower_band = current_price * (1 - 0.07)
        upper_band = current_price * (1 + 0.13)
        
        tab1, tab2, tab3, tab4 = st.tabs(["Scan & Forecast", "Signal Card", "Regime & News", "Strategy Lab"])
        
        with tab1:  # Scan & Forecast
            st.metric("Current Live Price", f"${current_price:,.2f}")
            
            # Real candlestick chart (historical data)
            if candles is not None and not candles.empty:
                fig_candle = go.Figure(data=[go.Candlestick(
                    x=candles['Date'],
                    open=candles['Open'],
                    high=candles['High'],
                    low=candles['Low'],
                    close=candles['Close'],
                    name="Price Action"
                )])
                fig_candle.update_layout(title="Last 60 Days - Candlestick Chart", height=380, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig_candle, use_container_width=True)
            else:
                st.info("Candlestick data loading…")
            
            # Polished confidence bands chart
            fig_band = go.Figure()
            fig_band.add_trace(go.Scatter(x=["Now", "1-5 Days"], y=[current_price, current_price * (1 + forecast_5d/100)],
                                        mode='lines+markers', name='Forecast', line=dict(color='#1f77b4', width=3)))
            fig_band.add_trace(go.Scatter(x=["1-5 Days"], y=[lower_band], mode='lines', name='Lower 95% Band',
                                        line=dict(dash='dash', color='#d62728')))
            fig_band.add_trace(go.Scatter(x=["1-5 Days"], y=[upper_band], mode='lines', name='Upper 95% Band',
                                        line=dict(dash='dash', color='#2ca02c')))
            fig_band.update_layout(
                title="1-5 Day Forecast with Polished Confidence Bands",
                height=340,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(t=50)
            )
            st.plotly_chart(fig_band, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("1-5 Day Forecast", f"+{forecast_5d}%")
            with col2: st.metric("Confidence", f"{confidence}%")
            with col3: st.metric("Regime", "Risk-On")
        
        with tab2:  # Signal Card (unchanged)
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
            account = st.number_input
