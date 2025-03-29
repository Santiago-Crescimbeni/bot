
from binance.client import Client


# Simulación para backtest o modo demo
def simulate_trade(entry_price, sl, tp, size_usdt, df, capital):
    next_row = df.iloc[-1]
    if next_row['high'] >= tp:
        gain = size_usdt * 0.02
        return "WIN", tp, capital + gain
    elif next_row['low'] <= sl:
        loss = size_usdt * 0.01
        return "LOSS", sl, capital - loss
    else:
        return "OPEN", next_row['close'], capital

# Decisión de ejecución

def execute_trade(mode, client, symbol, entry_price, sl, tp, size_usdt, df, capital, risk_pct=0.01):
    if mode == "live":
        return execute_live_trade(client, symbol, entry_price, sl, tp, capital, risk_pct)
    else:
        return simulate_trade(entry_price, sl, tp, size_usdt, df, capital)

# 🛠️ Ejecuta orden real en Binance Futures

def execute_live_trade(client: Client, symbol: str, entry_price: float, sl: float, tp: float, capital: float, risk_pct: float):
    quantity = round((capital * risk_pct) / entry_price, 3)  # Ej: 1000 USDT * 1% / precio

    try:
        print(f"🚀 Ejecutando orden REAL en Binance Futures: {symbol}")
        print(f"➡️ Entrada: {entry_price:.2f} | TP: {tp:.2f} | SL: {sl:.2f} | Qty: {quantity}")

        # 1️⃣ Orden de entrada tipo MARKET
        order = client.futures_create_order(
            symbol=symbol,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity
        )

        # 2️⃣ Orden de Stop Loss (STOP_MARKET)
        client.futures_create_order(
            symbol=symbol,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_STOP_MARKET,
            stopPrice=round(sl, 2),
            quantity=quantity,
            timeInForce="GTC"
        )

        # 3️⃣ Orden de Take Profit (TAKE_PROFIT_MARKET)
        client.futures_create_order(
            symbol=symbol,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_TAKE_PROFIT_MARKET,
            stopPrice=round(tp, 2),
            quantity=quantity,
            timeInForce="GTC"
        )

        print("✅ Orden REAL ejecutada con éxito ✅")
        return order

    except Exception as e:
        print(f"❌ Error al ejecutar orden real: {e}")
        return None
