import pandas as pd
import os

def analyze_trades():
    if not os.path.exists("trade_log.csv"):
        print("⚠️ No hay registros de trades aún para analizar.")
        return

    df = pd.read_csv("trade_log.csv")
    df.dropna(inplace=True)
    df['result'] = df['result'].astype(str)

    if 'score' not in df.columns or 'risk_pct' not in df.columns:
        print("⚠️ El archivo no tiene score/risk_pct registrado. Actualiza el logger.")
        return

    df['score_bucket'] = pd.cut(df['score'], bins=[0,30,50,65,80,100], labels=["0–30","30–50","50–65","65–80","80–100"])
    df['is_win'] = df['result'].str.contains("WIN").astype(int)

    summary = df.groupby("score_bucket").agg(
        trades=("result", "count"),
        win_rate=("is_win", "mean"),
        avg_risk=("risk_pct", "mean"),
        avg_capital=("capital", "mean")
    )
    summary["win_rate"] = summary["win_rate"] * 100

    print("📊 Rendimiento por score:")
    print(summary.round(2))

    best_bucket = summary["win_rate"].idxmax()
    print(f"🏆 Mejor score para operar: {best_bucket}")


# Para test manual:
if __name__ == "__main__":
    analyze_trades()
