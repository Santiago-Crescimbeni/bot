import os
from dotenv import load_dotenv
from binance.client import Client
import pandas as pd

# 📥 Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
TRADING_MODE = os.getenv("TRADING_MODE", "simulated")

# 🔌 Inicializar cliente Binance
client = Client(API_KEY, API_SECRET)

# 🔁 Si estamos en modo live pero usando TESTNET
if TRADING_MODE == "live_testnet":
    client.API_URL = "https://testnet.binancefuture.com"
    print("🧪 Modo TESTNET habilitado en Binance Futures")
else:
    print("📡 Conectado a Binance REAL")

# 📊 Obtener datos de mercado (para backtest o streaming)
def get_market_data(symbol, interval, limit):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df
