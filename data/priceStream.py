import websocket
import json
import threading

class PriceStream:
    def __init__(self, symbol, on_price_callback):
        self.symbol = symbol.lower()
        self.ws_url = f"wss://fstream.binance.com/ws/{self.symbol}@markPrice"
        self.on_price_callback = on_price_callback
        self.ws = None

    def on_message(self, ws, message):
        data = json.loads(message)
        price = float(data['p'])
        self.on_price_callback(price)

    def on_error(self, ws, error):
        print(f"❌ WebSocket Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("🔌 WebSocket cerrado")

    def on_open(self, ws):
        print("✅ WebSocket conectado a flujo de precio")

    def start(self):
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        threading.Thread(target=self.ws.run_forever).start()

    def stop(self):
        if self.ws:
            self.ws.close()
