import time
import pandas as pd
from datetime import datetime, timedelta

from engines.executor import Executor
from ai.predictor import AIPredictor
import backtrader as bt
from backtrader.feeds import PandasData
import yfinance as yf

# Configuration
tickers = ["SNDL", "NOK"]  # List of penny stocks to monitor
cash_per_trade = 1000  # USD allocation per signal
interval_seconds = 60  # Time between checks
history_period = "1d"  # Historical period for predictor

# Initialize components
executor = Executor(tickers, host='127.0.0.1', port=7497, clientId=1)
predictor = AIPredictor(tickers)
# Train AI models once at start
predictor.train_finrl_agent()
predictor.train_qlib_strategy()

try:
    print("Bot started at", datetime.now())
    while True:
        now = datetime.now()
        # Define window for current data fetch
        start = (now - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        end = now.strftime("%Y-%m-%d %H:%M:%S")
        # Fetch minute-level price data via yfinance
        df = yf.download(tickers, period=history_period, interval='1m', group_by='ticker', start=start, end=end)
        # Convert to multi-index DataFrame suitable for predictor
        # Assuming predictor handles expected format
        signals = predictor.predict_signals(df)
        print(f"{now} Signals:", signals)
        # Execute signals
        executed = executor.execute_signals(df)
        for sym, trade in executed.items():
            if trade:
                print(f"Executed {trade.order.action} for {sym} at {trade.orderStatus.avgFillPrice}")
        # Sleep until next interval
        time.sleep(interval_seconds)

except KeyboardInterrupt:
    print("Stopping bot...")

finally:
    executor.disconnect()
    print("Clean disconnection.")
