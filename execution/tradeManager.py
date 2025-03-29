from bot.data.priceStream import PriceStream

class TradeManager:
    def __init__(self, entry, sl, tp, size_usdt, capital, on_result):
        self.entry = entry
        self.sl = sl
        self.tp = tp
        self.partial_tp = entry + (tp - entry) * 0.5
        self.trailing_start = tp - (tp - entry) * 0.3
        self.size = size_usdt
        self.capital = capital
        self.hit_partial = False
        self.trailing_active = False
        self.on_result = on_result

    def on_price(self, price):
        if not self.hit_partial and price >= self.partial_tp:
            print(f"🟡 TP Parcial alcanzado: {self.partial_tp:.2f} — SL movido a break-even")
            self.sl = self.entry
            self.hit_partial = True

        if self.hit_partial and price >= self.trailing_start and not self.trailing_active:
            self.trailing_active = True
            print(f"🟢 Trailing SL activado desde: {self.trailing_start:.2f}")

        if self.trailing_active:
            trail_buffer = (self.tp - self.entry) * 0.1
            new_sl = price - trail_buffer
            if new_sl > self.sl:
                print(f"🔁 SL dinámico actualizado: {self.sl:.2f} → {new_sl:.2f}")
                self.sl = new_sl

        if price >= self.tp:
            gain = self.size * 0.02
            new_cap = self.capital + gain
            self.on_result("WIN", self.tp, new_cap)

        elif price <= self.sl:
            loss = self.size * 0.01 if not self.hit_partial else 0
            new_cap = self.capital - loss
            self.on_result("LOSS", self.sl, new_cap)

    def start_stream(self):
        self.stream = PriceStream("btcusdt", self.on_price)
        self.stream.start()

    def stop_stream(self):
        self.stream.stop()