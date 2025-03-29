import ta

def apply_indicators(df):
    df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
    df['ema_9'] = ta.trend.EMAIndicator(close=df['close'], window=9).ema_indicator()
    df['ema_21'] = ta.trend.EMAIndicator(close=df['close'], window=21).ema_indicator()
    return df
