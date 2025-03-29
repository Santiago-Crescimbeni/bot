def detect_liquidity_zones(df, threshold=3):
    highs = df['high'].round(2)
    lows = df['low'].round(2)

    eqh = highs.value_counts()[highs.value_counts() >= threshold].index.tolist()
    eql = lows.value_counts()[lows.value_counts() >= threshold].index.tolist()

    return eqh, eql
