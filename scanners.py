import yfinance as yf
import pandas as pd
import numpy as np

def calculate_rsi(data: pd.Series, window: int = 3) -> pd.Series:
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

def estimate_reversion_days(df: pd.DataFrame, sma_col: str) -> float:
    under_sma = df['Close'] < df[sma_col]
    blocks = (~under_sma).cumsum()[under_sma]
    if blocks.empty:
        return 1.0 
    return float(blocks.value_counts().mean())

def execute_penny_scan(tickers: list) -> list:
    results = []
    data = yf.download(tickers, period="1y", group_by="ticker", threads=True)
    
    for ticker_symbol in tickers:
        try:
            df = data[ticker_symbol] if len(tickers) > 1 else data
            df = df.dropna()
            
            if df.empty or len(df) < 200:
                continue
                
            df['SMA_fast'] = df['Close'].rolling(window=5).mean()
            df['STD_fast'] = df['Close'].rolling(window=5).std()
            df['RSI_fast'] = calculate_rsi(df['Close'], window=3)
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            
            df = df.dropna()
            if df.empty:
                continue
                
            current_price = float(df['Close'].iloc[-1])
            current_sma_fast = float(df['SMA_fast'].iloc[-1])
            current_std_fast = float(df['STD_fast'].iloc[-1])
            current_rsi_fast = float(df['RSI_fast'].iloc[-1])
            current_sma_200 = float(df['SMA_200'].iloc[-1])
            
            max_entry_threshold = current_sma_fast - (0.5 * current_std_fast)
            expected_margin = current_sma_fast - current_price
            
            is_price_extended = current_price <= max_entry_threshold
            is_rsi_oversold = current_rsi_fast <= 45 
            is_macro_uptrend = current_price > current_sma_200
            is_minimum_margin = expected_margin >= 0.05 
            
            if is_price_extended and is_rsi_oversold and is_minimum_margin and is_macro_uptrend:
                est_days = estimate_reversion_days(df, 'SMA_fast')
                results.append({
                    "symbol": ticker_symbol,
                    "current_price": round(current_price, 2),
                    "target_exit": round(current_sma_fast, 2),
                    "expected_margin": round(expected_margin, 2),
                    "est_days": round(est_days, 1)
                })
        except Exception:
            continue
            
    return results