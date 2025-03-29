def check_signal(df):
    last = df.iloc[-2]
    prev = df.iloc[-3]

    if last['rsi'] < 30 and prev['rsi'] < 30 and prev['ema_9'] < prev['ema_21'] and last['ema_9'] > last['ema_21']:
        return True
    return False