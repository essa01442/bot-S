```python
import time
import pandas as pd
from datetime import datetime, timedelta

from engines.executor import Executor
from ai.predictor import AIPredictor
from core.risk_manager import RiskManager
import yfinance as yf

# Configuration
tickers = ["SNDL", "NOK"]
cash_per_trade = 1000  # USD allocation per signal
interval_seconds = 60  # Time between checks
history_minutes = 5    # Lookback window
prepost = True         # Include pre/post-market data

# Initialize components
executor = Executor(
    tickers,
    host='127.0.0.1', port=7497, clientId=1
)
predictor = AIPredictor(tickers)
risk_manager = RiskManager()

# Train AI models once at start
predictor.train_finrl_agent()
predictor.train_qlib_strategy()

try:
    print("Bot started at", datetime.now())
    while True:
        now = datetime.now()
        start_dt = now - timedelta(minutes=history_minutes)
        # Fetch minute-level data with pre/post-market if desired
        df = yf.download(
            tickers,
            start=start_dt.strftime("%Y-%m-%d %H:%M:%S"),
            end=now.strftime("%Y-%m-%d %H:%M:%S"),
            interval='1m',
            group_by='ticker',
            prepost=prepost
        )
        # Generate AI signals
        signals = predictor.predict_signals(df)
        print(f"{now} Signals: {signals}")
        # Execute signals
        executed = executor.execute_signals(df)
        # Update risk manager and log performance
        for sym, trade in executed.items():
            if trade:
                price = trade.orderStatus.avgFillPrice or trade.orderStatus.lastFillPrice
                risk_manager.record_trade(sym, trade.order.action, price)
                print(f"Executed {trade.order.action} for {sym} at {price}")
        # Display risk metrics
        metrics = risk_manager.metrics()
        print(f"Current Drawdown: {metrics['drawdown']:.2%}", \
              f"Max Drawdown: {metrics['max_drawdown']:.2%}")
        # Sleep until next check
        time.sleep(interval_seconds)

except KeyboardInterrupt:
    print("Stopping bot...")

finally:
    executor.disconnect()
    # Export final metrics and trades
    risk_manager.generate_report('reports/risk_report.html')
    print("Clean disconnection.")
```
