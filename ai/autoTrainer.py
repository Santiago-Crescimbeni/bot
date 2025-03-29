import os
import pandas as pd
from bot.ai.trainModel import train_trade_classifier

STATE_FILE = "bot/ai/last_train_state.txt"


def get_last_train_count():
    if not os.path.exists(STATE_FILE):
        return 0
    with open(STATE_FILE, "r") as file:
        return int(file.read())


def update_train_count(count):
    with open(STATE_FILE, "w") as file:
        file.write(str(count))


def auto_train_model(threshold=50):
    if not os.path.exists("trade_log.csv"):
        print("⚠️ No hay trade_log.csv para evaluar entrenamiento automático.")
        return

    df = pd.read_csv("trade_log.csv")
    total_trades = len(df)
    last_trained = get_last_train_count()

    if total_trades - last_trained >= threshold:
        print(f"📈 Se alcanzaron {total_trades - last_trained} nuevos trades. Entrenando modelo...")
        train_trade_classifier()
        update_train_count(total_trades)
    else:
        print(f"⏳ Solo {total_trades - last_trained} nuevos trades. No se entrena todavía.")


if __name__ == "__main__":
    auto_train_model()