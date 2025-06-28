import os
import pandas as pd
from datetime import datetime

class RiskManager:
    """
    Manages risk by tracking trades, computing drawdowns, and generating reports.
    """
    def __init__(self):
        # Dataframe to store trades
        self.trades = pd.DataFrame(columns=[
            'timestamp', 'symbol', 'action', 'price'
        ])
        # Track peak equity
        self.equity_curve = []
        self.current_equity = 0
        self.peak_equity = 0

    def record_trade(self, symbol: str, action: str, price: float):
        """
        Record a trade execution.
        """
        timestamp = datetime.utcnow()
        self.trades = self.trades.append({
            'timestamp': timestamp,
            'symbol': symbol,
            'action': action,
            'price': price
        }, ignore_index=True)
        # Update equity: simple PnL per trade
        pnl = price * (1 if action.lower() == 'sell' else -1)
        self.current_equity += pnl
        self.peak_equity = max(self.peak_equity, self.current_equity)
        # Record equity curve
        self.equity_curve.append((timestamp, self.current_equity))

    def metrics(self) -> dict:
        """
        Compute current drawdown and max drawdown.
        """
        if not self.equity_curve:
            return {'drawdown': 0.0, 'max_drawdown': 0.0}
        # Compute drawdowns
        df = pd.DataFrame(self.equity_curve, columns=['timestamp', 'equity'])
        rolling_max = df['equity'].cummax()
        drawdowns = (rolling_max - df['equity']) / rolling_max
        return {
            'drawdown': drawdowns.iloc[-1],
            'max_drawdown': drawdowns.max()
        }

    def generate_report(self, path: str):
        """
        Generate an HTML report of risk metrics and trade history.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        html = []
        html.append(f"<h1>Risk Report - {datetime.utcnow().isoformat()}</h1>")
        meters = self.metrics()
        html.append(f"<p>Current Drawdown: {meters['drawdown']:.2%}</p>")
        html.append(f"<p>Max Drawdown: {meters['max_drawdown']:.2%}</p>")
        html.append("<h2>Trades</h2>")
        html.append(self.trades.to_html(index=False, classes='table'))
        with open(path, 'w') as f:
            f.write("\n".join(html))
        return path
