import joblib
import os
import pandas as pd

# Carga el modelo entrenado
MODEL_PATH = "bot/ai/tradeClassifier.pkl"
model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

def predict_trade(features_dict):
    if not model:
        print("⚠️ Modelo ML no disponible. Ejecutá trainModel.py primero.")
        return 1  # Por defecto, permitir operar

    df = pd.DataFrame([features_dict])

    # Preprocesamiento igual que en el entrenamiento
    df['signal'] = df['signal'].astype(bool).astype(int)
    df['confirmation'] = df['confirmation'].astype(bool).astype(int)
    df['structure'] = df['structure'].map({'BULLISH': 1, 'BEARISH': 0})
    df['trend'] = df['trend'].map({'BULLISH': 1, 'BEARISH': 0, None: 0})

    X = df[['score', 'risk_pct', 'signal', 'confirmation', 'structure', 'volume', 'trend']]
    prediction = model.predict(X)[0]  # 1 = WIN probable, 0 = evitar

    return prediction

# 🧪 Test manual
if __name__ == "__main__":
    test = {
        "score": 85,
        "risk_pct": 0.02,
        "signal": True,
        "confirmation": True,
        "structure": "BULLISH",
        "volume": 3200,
        "trend": "BULLISH"
    }
    print("✅ Predicción ML:", predict_trade(test))