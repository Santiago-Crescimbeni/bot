def get_market_structure(df):
    df['swing_high'] = df['high'][(df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(-1))]
    df['swing_low'] = df['low'][(df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(-1))]

    recent_highs = df['swing_high'].dropna().tail(2)
    recent_lows = df['swing_low'].dropna().tail(2)
    close = df['close'].iloc[-2]

    structure = "RANGE"
    choch = False

    if len(recent_highs) == 2 and close > recent_highs.iloc[-2]:
        structure = "BULLISH"
    elif len(recent_lows) == 2 and close < recent_lows.iloc[-2]:
        structure = "BEARISH"

    if len(recent_highs) == 2 and len(recent_lows) == 2:
        if recent_highs.iloc[-1] < recent_highs.iloc[-2] and close < recent_lows.iloc[-2]:
            choch = True  # Cambio bajista
        elif recent_lows.iloc[-1] > recent_lows.iloc[-2] and close > recent_highs.iloc[-2]:
            choch = True  # Cambio alcista

    return structure, choch