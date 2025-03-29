class RiskManager:
    def __init__(self, capital, risk_pct):
        self.capital = capital
        self.risk_pct = risk_pct
        self.tp_pct = 0.02
        self.sl_pct = 0.01

    def calculate_trade_params(self, entry_price):
        tp = entry_price * (1 + self.tp_pct)
        sl = entry_price * (1 - self.sl_pct)
        size = self.capital * self.risk_pct
        return sl, tp, size
