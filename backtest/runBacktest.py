from bot.data.downloadHistoricalData import save_klines_to_csv
from bot.backtest.backtester import run_backtest
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

def run_full_backtest():
    filename = "historical_data.csv"
    print("⏳ Descargando datos históricos de BTC/USDT (15m)...")
    save_klines_to_csv(symbol="BTCUSDT", interval="15m", filename=filename, start="2023-01-01", end="2023-12-31")

    print("🚀 Ejecutando backtest completo...")
    run_backtest(csv_path=filename)

    # 📄 Generar reporte desde trade_log
    log_file = "trade_log.csv"
    if not os.path.exists(log_file):
        print("⚠️ No se encontró trade_log.csv para analizar.")
        return

    df = pd.read_csv(log_file)
    df = df[df["result"].str.contains("BT-BTCUSDT")]  # Solo resultados del backtest actual
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    df.to_csv("backtest_report.csv", index=False)
    print("📁 Reporte guardado en backtest_report.csv")

    # 📊 Métricas de rendimiento
    if not df.empty:
        start_capital = df["capital"].iloc[0]
        end_capital = df["capital"].iloc[-1]
        growth_pct = ((end_capital - start_capital) / start_capital) * 100
        win_rate = len(df[df["result"].str.contains("WIN")]) / len(df) * 100
        total_trades = len(df)

        print(f"\n📈 RESUMEN BACKTEST")
        print(f"📌 Capital inicial: {start_capital:.2f} USDT")
        print(f"📌 Capital final:   {end_capital:.2f} USDT")
        print(f"📌 Crecimiento:     {growth_pct:.2f}%")
        print(f"📌 Trades totales:  {total_trades}")
        print(f"📌 Win rate:        {win_rate:.2f}%\n")

        # Guardar resumen como fila en CSV
        summary_file = "backtest_summary.csv"
        summary_data = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "capital_inicial": round(start_capital, 2),
            "capital_final": round(end_capital, 2),
            "crecimiento_pct": round(growth_pct, 2),
            "win_rate": round(win_rate, 2),
            "trades_totales": total_trades
        }
        df_summary = pd.DataFrame([summary_data])
        if not os.path.exists(summary_file):
            df_summary.to_csv(summary_file, index=False)
        else:
            df_summary.to_csv(summary_file, mode='a', header=False, index=False)

        print(f"🧾 Resumen guardado en {summary_file}")

        # 📈 Graficar curva de capital
        plt.figure(figsize=(10, 5))
        plt.plot(df["timestamp"], df["capital"], label="Capital", color="green")
        plt.title("Evolución del Capital - Backtest")
        plt.xlabel("Tiempo")
        plt.ylabel("Capital USDT")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("backtest_equity_curve.png")
        plt.show()
        print("📊 Curva de capital guardada como backtest_equity_curve.png")

if __name__ == '__main__':
    run_full_backtest()
