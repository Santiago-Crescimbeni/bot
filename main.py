from bot.data.binanceData import get_market_data
from bot.indicator.indicator import apply_indicators
from bot.strategies.signalEngine import check_signal
from bot.execution.tradeExecutor import execute_trade
from bot.execution.tradeManager import TradeManager
from bot.risk.riskManage import RiskManager
from bot.util.logger import save_log
from bot.structure.marketStructure import get_market_structure
from bot.structure.liquidityZones import detect_liquidity_zones
from bot.structure.orderBlocks import detect_order_blocks
from bot.structure.fairValueGaps import detect_fvg
from bot.structure.candleConfirmations import candle_confirmation
from bot.util.timeUtils import in_killzone
from bot.data.sentimentData import get_market_sentiment
from bot.ai.predictor import predict_trade
from bot.ai.autoTrainer import auto_train_model

import datetime
import os
from dotenv import load_dotenv
from binance.client import Client

load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

START_CAPITAL = float(os.getenv("START_CAPITAL", 1000))
DRAWDOWN_LIMIT = float(os.getenv("DRAWDOWN_LIMIT", 0.15))
WITHDRAW_PROFIT = float(os.getenv("WITHDRAW_PROFIT", 0.30))
TRADING_MODE = os.getenv("TRADING_MODE", "simulated")

capital_dict = {
    "BTCUSDT": START_CAPITAL,
    "ETHUSDT": START_CAPITAL,
    "SOLUSDT": START_CAPITAL
}

max_capital_dict = capital_dict.copy()


def get_dynamic_risk(score):
    if score >= 80:
        return 0.02
    elif score >= 60:
        return 0.015
    elif score >= 40:
        return 0.01
    else:
        return 0.005


def check_risk_controls(symbol, current_capital):
    global capital_dict, max_capital_dict
    max_cap = max_capital_dict[symbol]
    drawdown = (max_cap - current_capital) / max_cap
    if drawdown > DRAWDOWN_LIMIT:
        print(f"🛑 [{symbol}] STOP: Drawdown excedido ({drawdown*100:.2f}%)")
        return False
    if current_capital > START_CAPITAL * (1 + WITHDRAW_PROFIT):
        withdraw_amount = current_capital - START_CAPITAL
        print(f"💸 [{symbol}] Retiro sugerido: {withdraw_amount:.2f} USDT")
    return True


def is_market_active(df):
    last_range = df.iloc[-1]['high'] - df.iloc[-1]['low']
    avg_range = df['high'].sub(df['low']).rolling(window=20).mean().iloc[-2]
    volume = df.iloc[-1]['volume']
    avg_volume = df['volume'].rolling(window=20).mean().iloc[-2]
    if last_range < 0.25 * avg_range and volume < 0.5 * avg_volume:
        print("⚠️ Mercado inactivo: bajo rango y volumen")
        return False
    return True


def run_symbol(symbol):
    print(f"\n📊 Ejecutando análisis para: {symbol}")
    now_utc = datetime.datetime.utcnow()
    if not in_killzone(now_utc):
        print("🕒 Fuera de killzone. No se evalúan entradas.")
        return

    sentiment, score = get_market_sentiment()
    if sentiment == "BEARISH":
        print("😨 Sentimiento negativo. Se evita operar en LONG.")
        return

    df = get_market_data(symbol, "15m", 100)
    if not is_market_active(df):
        return

    df = apply_indicators(df)

    structure, trend_change = get_market_structure(df)
    eqh, eql = detect_liquidity_zones(df)
    order_blocks = detect_order_blocks(df)
    fvg_zones = detect_fvg(df)
    candle_confirm = candle_confirmation(df)
    signal = check_signal(df)

    valid_confluence = False
    features = {
        "structure": structure,
        "signal": signal,
        "confirmation": candle_confirm,
        "ob_range": str(order_blocks[-1]) if order_blocks else None,
        "fvg_range": str(fvg_zones[-1]) if fvg_zones else None,
        "volume": df.iloc[-1]['volume'],
        "trend": trend_change,
        "score": score,
        "risk_pct": get_dynamic_risk(score)
    }

    if structure == "BULLISH" and signal and candle_confirm:
        last_ob = order_blocks[-1] if order_blocks else None
        last_fvg = fvg_zones[-1] if fvg_zones else None
        last_price = df.iloc[-2]['close']

        if last_ob and last_fvg:
            ob_range = (last_ob['low'], last_ob['high'])
            fvg_range = (last_fvg['low'], last_fvg['high'])
            in_ob = ob_range[0] <= last_price <= ob_range[1]
            in_fvg = fvg_range[0] <= last_price <= fvg_range[1]
            if in_ob or in_fvg:
                valid_confluence = True

    if valid_confluence:
        prediction = predict_trade(features)
        if prediction != 1:
            print(f"❌ [{symbol}] Predicción ML desfavorable. Trade descartado.")
            return

        capital = capital_dict[symbol]
        risk_pct = features['risk_pct']
        risk_mgr = RiskManager(capital, risk_pct)
        entry_price = df.iloc[-2]['close']
        sl, tp, size = risk_mgr.calculate_trade_params(entry_price)

        def on_trade_result(result, exit_price, new_cap):
            capital_dict[symbol] = new_cap
            if new_cap > max_capital_dict[symbol]:
                max_capital_dict[symbol] = new_cap
            if not check_risk_controls(symbol, new_cap):
                return
            save_log(entry_price, exit_price, result + f"-{symbol}", new_cap, score, risk_pct, features)
            print(f"✅ [{symbol}] Trade cerrado: {result} | Capital actualizado: {new_cap:.2f}")

        result = execute_trade(
            mode=TRADING_MODE,
            client=client,
            symbol=symbol,
            entry_price=entry_price,
            sl=sl,
            tp=tp,
            size_usdt=size,
            df=df,
            capital=capital
        )

        manager = TradeManager(entry_price, sl, tp, size, capital, on_trade_result)
        manager.start_stream()

    else:
        print(f"⏸️ [{symbol}] Sin confluencia válida institucional para entrada.")


if __name__ == "__main__":
    import time
    while True:
        for symbol in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
            try:
                run_symbol(symbol)
            except Exception as e:
                print(f"❌ Error en símbolo {symbol}: {e}")
        auto_train_model()
        print("🔁 Esperando 5 minutos...")
        time.sleep(300)
