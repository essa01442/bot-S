import backtrader as bt

class ScalpingStrategy(bt.Strategy):
    params = dict(
        fast=9,
        slow=21,
        stop_loss=0.015,
        take_profit=0.03,
    )

    def __init__(self):
        self.ema_fast = bt.ind.EMA(self.data.close, period=self.p.fast)
        self.ema_slow = bt.ind.EMA(self.data.close, period=self.p.slow)
        self.order = None

    def next(self):
        if self.order:
            return

        price = self.data.close[0]
        if not self.position:
            # دخول عند تقاطع EMA صاعد
            if self.ema_fast[0] > self.ema_slow[0] and self.ema_fast[-1] <= self.ema_slow[-1]:
                size = self.broker.getcash() * 0.1 / price
                self.order = self.buy(size=size)
        else:
            entry_price = self.position.price
            # وقف الخسارة
            if price < entry_price * (1 - self.p.stop_loss):
                self.order = self.sell()
            # جني الربح
            elif price > entry_price * (1 + self.p.take_profit):
                self.order = self.sell()
feat: add scalping strategy
