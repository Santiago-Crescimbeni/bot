import csv
import os
from datetime import datetime

def save_log(entry_price, exit_price, result, capital, score=None, risk_pct=None, features=None):
    file_exists = os.path.isfile("trade_log.csv")
    with open("trade_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "timestamp", "entry_price", "exit_price", "result", "capital",
                "score", "risk_pct", "structure", "signal", "confirmation",
                "ob_range", "fvg_range", "volume", "trend"
            ])
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            round(entry_price, 2),
            round(exit_price, 2),
            result,
            round(capital, 2),
            score if score is not None else "",
            round(risk_pct * 100, 2) if risk_pct is not None else "",
        ]
        # features opcionales (para ML futuro)
        row += [
            features.get("structure", ""),
            features.get("signal", ""),
            features.get("confirmation", ""),
            features.get("ob_range", ""),
            features.get("fvg_range", ""),
            features.get("volume", ""),
            features.get("trend", "")
        ] if features else ["" for _ in range(7)]
        writer.writerow(row)
