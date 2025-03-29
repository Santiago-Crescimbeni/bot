import requests

def get_market_sentiment():
    try:
        # --- 1. Fear & Greed Index ---
        fng = requests.get("https://api.alternative.me/fng/", timeout=5).json()
        fng_score = int(fng['data'][0]['value'])
        fng_sentiment = "BULLISH" if fng_score >= 60 else "BEARISH" if fng_score <= 30 else "NEUTRAL"

        # --- 2. BTC Dominance ---
        dominance_data = requests.get("https://api.coingecko.com/api/v3/global", timeout=5).json()
        btc_dominance = dominance_data['data']['market_cap_percentage']['btc']
        dominance_sentiment = "BULLISH" if btc_dominance < 45 else "BEARISH" if btc_dominance > 55 else "NEUTRAL"
        dominance_score = 100 - int(btc_dominance)

        # --- 3. SOPR Proxy ---
        sopr_resp = requests.get("https://api.blockchain.com/v3/exchange/tickers/BTC-USD", timeout=5)
        sopr_value = sopr_resp.json().get("price_24h", 1.0)
        onchain_sentiment = "BULLISH" if sopr_value > 1.0 else "BEARISH" if sopr_value < 0.95 else "NEUTRAL"
        sopr_score = int((sopr_value / 1.0) * 50) + 50 if sopr_value > 1.0 else int((sopr_value / 1.0) * 50)
        sopr_score = max(0, min(100, sopr_score))

        # Consolida
        score_final = int((fng_score + dominance_score + sopr_score) / 3)

        print(f"📊 Sentimientos → F&G: {fng_sentiment} ({fng_score}) | Dominance: {dominance_sentiment} ({btc_dominance:.2f}%) | SOPR: {onchain_sentiment} ({sopr_value:.2f})")
        print(f"📈 Score Consolidado: {score_final}/100")

        # Clasificación + Retorno del score
        if score_final >= 65:
            sentiment = "BULLISH"
        elif score_final <= 35:
            sentiment = "BEARISH"
        else:
            sentiment = "NEUTRAL"

        return sentiment, score_final

    except Exception as e:
        print(f"⚠️ Error al obtener datos de sentimiento externo: {e}")
        return "NEUTRAL", 50