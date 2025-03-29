def detect_fvg(df):
    fvg_list = []
    for i in range(2, len(df)):
        prev_candle = df.iloc[i - 2]
        curr_candle = df.iloc[i]

        if curr_candle['low'] > prev_candle['high']:
            fvg = {
                "index": df.index[i],
                "low": prev_candle['high'],
                "high": curr_candle['low']
            }
            fvg_list.append(fvg)

    return fvg_list
