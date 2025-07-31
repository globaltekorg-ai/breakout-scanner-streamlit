import streamlit as st
import pandas as pd
import yfinance as yf
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

st.set_page_config(page_title="Breakout Scanner", layout="wide")
st.title("🔥 Breakout-Ready Stock Scanner (EMA + Volume + MACD + RSI + BB Squeeze)")

symbols_input = st.text_input("Enter comma-separated NSE symbols (e.g., RELIANCE.NS, INFY.NS)", "RELIANCE.NS, TCS.NS, INFY.NS")
symbols = [sym.strip().upper() for sym in symbols_input.split(',') if sym.strip()]

result = []

@st.cache_data(show_spinner=False)
def get_data(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d")
        return df
    except Exception as e:
        return None

def analyze_stock(symbol):
    df = get_data(symbol)
    if df is None or df.empty:
        return f"{symbol}: Failed to fetch data."

    df.dropna(inplace=True)

    try:
        df['EMA_10'] = EMAIndicator(df['Close'], window=10).ema_indicator()
        df['EMA_20'] = EMAIndicator(df['Close'], window=20).ema_indicator()
        df['EMA_50'] = EMAIndicator(df['Close'], window=50).ema_indicator()
        df['EMA_100'] = EMAIndicator(df['Close'], window=100).ema_indicator()
        df['EMA_200'] = EMAIndicator(df['Close'], window=200).ema_indicator()

        macd = MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()

        rsi = RSIIndicator(df['Close'])
        df['RSI'] = rsi.rsi()

        bb = BollingerBands(df['Close'])
        df['bb_bbm'] = bb.bollinger_mavg()
        df['bb_bbh'] = bb.bollinger_hband()
        df['bb_bbl'] = bb.bollinger_lband()

        latest = df.iloc[-1]

        squeeze = latest['bb_bbh'] - latest['bb_bbl'] < (0.05 * latest['Close'])
        rsi_break = latest['RSI'] > 50
        macd_cross = latest['MACD'] > latest['MACD_Signal']
        volume_surge = latest['Volume'] > df['Volume'].rolling(window=10).mean().iloc[-1]

        emas = [latest['EMA_10'], latest['EMA_20'], latest['EMA_50'], latest['EMA_100'], latest['EMA_200']]
        ema_converging = max(emas) - min(emas) < (0.03 * latest['Close'])

        if all([squeeze, rsi_break, macd_cross, volume_surge, ema_converging]):
            return f"✅ {symbol} is a breakout candidate!"
        else:
            return None

    except Exception as e:
        return f"{symbol}: Error - {str(e)}"

st.markdown("---")
st.subheader("Scanner Output:")

with st.spinner("Analyzing stocks..."):
    for symbol in symbols:
        result_str = analyze_stock(symbol)
        if result_str:
            st.success(result_str)

if not any(analyze_stock(sym) for sym in symbols):
    st.info("No breakout candidates found at the moment.")
