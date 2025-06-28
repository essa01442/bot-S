import backtrader as bt

class Backtester:
    def __init__(self, data_feed, strategy, cash=10000):
        self.cerebro = bt.Cerebro(stdstats=False)
        self.cerebro.broker.setcash(cash)
        self.cerebro.addstrategy(strategy)
        self.cerebro.adddata(data_feed)

    def run(self):
        return self.cerebro.run()

    def plot(self, **kwargs):
        self.cerebro.plot(**kwargs)
feat: add Backtester engine wrapper
