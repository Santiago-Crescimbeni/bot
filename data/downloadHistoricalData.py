import requests
import pandas as pd
import time

def get_binance_klines(symbol, interval, start_time, end_time, limit=1000):
    url = 'https://api.binance.com/api/v3/klines'
    data = []
    while start_time < end_time:
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_time,
            'endTime': end_time,
            'limit': limit
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error en la solicitud: {response.status_code}")
        klines = response.json()
        if not klines:
            break
        data.extend(klines)
        start_time = klines[-1][0] + 1
        time.sleep(0.1)
    return data

def save_klines_to_csv(symbol='BTCUSDT', interval='15m', filename='historical_data.csv',
                       start='2023-01-01', end='2023-12-31'):
    start_time = int(pd.Timestamp(start).timestamp() * 1000)
    end_time = int(pd.Timestamp(end).timestamp() * 1000)
    klines = get_binance_klines(symbol, interval, start_time, end_time)

    columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
               'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
               'Taker buy quote asset volume', 'Ignore']
    df = pd.DataFrame(klines, columns=columns)
    df.to_csv(filename, index=False)
    print(f"✅ Datos históricos guardados en {filename}")

if __name__ == '__main__':
    save_klines_to_csv()