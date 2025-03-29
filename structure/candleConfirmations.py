def candle_confirmation(df):
    last = df.iloc[-2]
    prev = df.iloc[-3]

    # Engulfing alcista
    bullish_engulfing = last['close'] > last['open'] and last['open'] < prev['close'] and last['close'] > prev['open']

    # Pin bar alcista
    body = abs(last['close'] - last['open'])
    wick = last['low'] - min(last['close'], last['open'])
    pin_bar = wick > 2 * body and last['close'] > last['open']

    return bullish_engulfing or pin_bar
