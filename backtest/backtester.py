import pandas as pd
from bot.indicator.indicator import apply_indicators
from bot.strategies.signalEngine import check_signal
from bot.structure.marketStructure import get_market_structure
from bot.structure.liquidityZones import detect_liquidity_zones
from bot.structure.orderBlocks import detect_order_blocks
from bot.structure.fairValueGaps import detect_fvg
from bot.structure.candleConfirmations import candle_confirmation
from bot.risk.riskManage import RiskManager
from bot.ai.predictor import predict_trade
from bot.util.logger import save_log


def run_backtest(csv_path, symbol="BTCUSDT", capital=1000):
    df = pd.read_csv(csv_path)
    df = df.rename(columns={"Open time": "timestamp", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df = df.set_index('timestamp')
    df = df.astype(float)

    df = apply_indicators(df)

    results = []
    for i in range(50, len(df) - 2):
        window = df.iloc[i-50:i+2].copy()
        structure, trend_change = get_market_structure(window)
        eqh, eql = detect_liquidity_zones(window)
        order_blocks = detect_order_blocks(window)
        fvg_zones = detect_fvg(window)
        candle_confirm = candle_confirmation(window)
        signal = check_signal(window)

        valid = False
        features = {
            "structure": structure,
            "signal": signal,
            "confirmation": candle_confirm,
            "ob_range": str(order_blocks[-1]) if order_blocks else None,
            "fvg_range": str(fvg_zones[-1]) if fvg_zones else None,
            "volume": window.iloc[-2]['volume'],
            "trend": trend_change,
            "score": 70,
            "risk_pct": 0.01
        }

        if structure == "BULLISH" and signal and candle_confirm:
            last_price = window.iloc[-2]['close']
            last_ob = order_blocks[-1] if order_blocks else None
            last_fvg = fvg_zones[-1] if fvg_zones else None

            in_zone = False
            if last_ob:
                in_zone |= last_ob['low'] <= last_price <= last_ob['high']
            if last_fvg:
                in_zone |= last_fvg['low'] <= last_price <= last_fvg['high']

            if in_zone:
                valid = True

        if valid:
            prediction = predict_trade(features)
            if prediction != 1:
                continue

            entry_price = window.iloc[-2]['close']
            risk_mgr = RiskManager(capital, features['risk_pct'])
            sl, tp, size = risk_mgr.calculate_trade_params(entry_price)
            next_row = window.iloc[-1]

            if next_row['high'] >= tp:
                capital += size * 0.02
                result = "WIN"
            elif next_row['low'] <= sl:
                capital -= size * 0.01
                result = "LOSS"
            else:
                result = "OPEN"

            save_log(entry_price, next_row['close'], f"{result}-BT-{symbol}", capital, 70, features['risk_pct'], features)
            results.append(result)

    print(f"🏁 Backtest finalizado: {len(results)} trades ejecutados. Capital final: {capital:.2f} USDT")


# 🧪 Uso:
if __name__ == "__main__":
    run_backtest("historical_data.csv")
