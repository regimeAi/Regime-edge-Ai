import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import time
import warnings

warnings.filterwarnings("ignore")

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Regime Edge AI",
    page_icon="📈",
    layout="wide"
)

st.title("📊 Regime Edge AI - Backtesting & Analysis")
st.markdown("**Advanced Trading Regime Detection & Backtesting**")

# ====================== SIDEBAR ======================
st.sidebar.header("Configuration")

ticker = st.sidebar.text_input("Ticker Symbol", value="SPY")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2026-04-01"))

if st.sidebar.button("Run Backtest"):
    with st.spinner("Fetching data and running backtest..."):
        try:
            # Fetch data
            import yfinance as yf
            data = yf.download(ticker, start=start_date, end=end_date)
            
            if data.empty:
                st.error("No data downloaded. Check ticker symbol.")
            else:
                # Simple regime detection example (you can expand this)
                data['Returns'] = data['Close'].pct_change()
                data['MA50'] = data['Close'].rolling(50).mean()
                data['Regime'] = np.where(data['Close'] > data['MA50'], 1, 0)
                
                # Linear Regression example
                X = np.arange(len(data)).reshape(-1, 1)
                y = data['Close'].values
                model = LinearRegression().fit(X, y)
                data['Trend'] = model.predict(X)
                
                # ====================== RESULTS ======================
                st.success(f"Backtest Results for {ticker} ({start_date} to {end_date})")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Return", f"{(data['Close'].iloc[-1]/data['Close'].iloc[0]-1)*100:.2f}%")
                with col2:
                    st.metric("Sharpe Ratio (approx)", f"{data['Returns'].mean() / data['Returns'].std() * np.sqrt(252):.2f}")
                
                # Charts
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price'))
                fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], name='50-day MA'))
                fig.add_trace(go.Scatter(x=data.index, y=data['Trend'], name='Linear Trend'))
                fig.update_layout(title=f"{ticker} Price & Regime", height=600)
                st.plotly_chart(fig, width="stretch")   # Fixed: use width instead of use_container_width
                
                # Data table
                st.subheader("Recent Data")
                st.dataframe(data.tail(100), width="stretch")   # Fixed
                
                # Backtest summary
                st.subheader("Regime Statistics")
                regime_stats = data['Regime'].value_counts(normalize=True) * 100
                st.bar_chart(regime_stats, width="stretch")
                
        except Exception as e:
            st.error(f"Error during backtest: {str(e)}")

# ====================== FOOTER ======================
st.caption("Regime Edge AI © 2026 | Built with Streamlit + yfinance + scikit-learn")
