def detect_order_blocks(df):
    blocks = []
    for i in range(2, len(df)-2):
        current = df.iloc[i]
        next_candle = df.iloc[i+1]

        if current['close'] < current['open'] and next_candle['close'] > next_candle['open']:
            # Vela bajista seguida de vela alcista con rompimiento
            if next_candle['high'] > max(df['high'].iloc[i-2:i+1]):
                block = {
                    "index": df.index[i],
                    "open": current['open'],
                    "low": current['low'],
                    "high": current['high']
                }
                blocks.append(block)

    return blocks