import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard del Bot de Trading", layout="wide")
st.title("📊 Dashboard de Trading Virtual - BTC/ETH/SOL")
st.markdown("---")

st.markdown("<meta http-equiv='refresh' content='10'>", unsafe_allow_html=True)

if os.path.exists("trade_log.csv"):
    df = pd.read_csv("trade_log.csv")
    df.dropna(inplace=True)

    total_trades = len(df)
    wins = len(df[df["result"].str.contains("WIN")])
    losses = len(df[df["result"].str.contains("LOSS")])
    open_trades = len(df[df["result"] == "OPEN"])
    final_capital = df["capital"].iloc[-1]
    initial_capital = df["capital"].iloc[0]
    profit = final_capital - initial_capital
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏁 Capital Inicial", f"${initial_capital:.2f}")
    col2.metric("💰 Capital Actual", f"${final_capital:.2f}", f"{profit:.2f}")
    col3.metric("📈 Trades Ganados", f"{wins}", f"{win_rate:.2f}%")
    col4.metric("📉 Trades Perdidos", f"{losses}")

    st.markdown("### 📉 Evolución del Capital")
    fig, ax = plt.subplots()
    ax.plot(df["timestamp"], df["capital"], marker='o', linestyle='-', color='blue')
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Capital (USDT)")
    ax.grid(True)
    st.pyplot(fig)

    if "score" in df.columns and "risk_pct" in df.columns:
        st.markdown("### 🧠 Score de Sentimiento y Riesgo")
        fig2, ax2 = plt.subplots()
        ax2.plot(df["timestamp"], df["score"], label="Score", color='orange')
        ax2.set_ylabel("Sentimiento (0-100)", color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')
        ax2.set_xlabel("Tiempo")

        ax3 = ax2.twinx()
        ax3.plot(df["timestamp"], df["risk_pct"], label="Risk %", color='green')
        ax3.set_ylabel("% Riesgo", color='green')
        ax3.tick_params(axis='y', labelcolor='green')

        st.pyplot(fig2)

        # 🔍 Análisis de performance por score
        df['score_bucket'] = pd.cut(df['score'], bins=[0,30,50,65,80,100], labels=["0–30","30–50","50–65","65–80","80–100"])
        df['is_win'] = df['result'].str.contains("WIN").astype(int)
        summary = df.groupby("score_bucket").agg(
            trades=("result", "count"),
            win_rate=("is_win", "mean"),
            avg_risk=("risk_pct", "mean"),
            avg_capital=("capital", "mean")
        )
        summary["win_rate"] = summary["win_rate"] * 100

        st.markdown("### 🧠 Rendimiento por Nivel de Score")
        st.dataframe(summary.round(2), use_container_width=True)

        best_bucket = summary["win_rate"].idxmax()
        suggested_risk = summary.loc[best_bucket]["avg_risk"]

        st.success(f"🏆 Mejor score para operar: {best_bucket} → Sugerencia: ajustar risk_pct a {round(suggested_risk * 100, 2)}%")

    st.markdown("### 🔄 Últimos 5 trades")
    st.dataframe(df.tail(5).iloc[::-1], use_container_width=True)

    st.success("El dashboard se actualiza cada 10 segundos. No toques nada 😉")
else:
    st.warning("Aún no hay trades registrados. Ejecutá el bot para generar el archivo `trade_log.csv`.")