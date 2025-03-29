import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def train_trade_classifier():
    if not os.path.exists("trade_log.csv"):
        print("❌ No se encontró trade_log.csv para entrenar.")
        return

    df = pd.read_csv("trade_log.csv")
    df.dropna(inplace=True)

    # 🎯 Target: si el trade fue ganado (WIN)
    df['target'] = df['result'].str.contains("WIN").astype(int)

    # 📥 Features seleccionados
    df['signal'] = df['signal'].astype(bool).astype(int)
    df['confirmation'] = df['confirmation'].astype(bool).astype(int)
    df['structure'] = df['structure'].map({'BULLISH': 1, 'BEARISH': 0})
    df['trend'] = df['trend'].map({'BULLISH': 1, 'BEARISH': 0, None: 0})

    features = ['score', 'risk_pct', 'signal', 'confirmation', 'structure', 'volume', 'trend']
    X = df[features]
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"✅ Modelo entrenado con {acc*100:.2f}% de precisión")
    print(classification_report(y_test, y_pred))

    joblib.dump(clf, "bot/ai/tradeClassifier.pkl")
    print("📦 Modelo guardado como tradeClassifier.pkl")


if __name__ == "__main__":
    train_trade_classifier()
