```python
import time
import pandas as pd
import logging
from datetime import datetime, timedelta

from engines.executor import Executor
from ai.predictor import AIPredictor
from core.risk_manager import RiskManager
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# Configuration
tickers = ["SNDL", "NOK"]
cash_per_trade = 1000      # USD allocation per signal
interval_seconds = 60      # Time between checks
history_minutes = 5        # Lookback window
prepost = True             # Include pre/post-market data
max_retries = 3            # Max retries on failure
retry_delay = 10           # Seconds between retries

# Initialize components outside loop for reuse
def init_components():
    executor = Executor(
        tickers,
        host='127.0.0.1', port=7497, clientId=1
    )
    predictor = AIPredictor(tickers)
    risk_manager = RiskManager()
    # Train AI models once at start
    predictor.train_finrl_agent()
    predictor.train_qlib_strategy()
    return executor, predictor, risk_manager

executor, predictor, risk_manager = init_components()

logger.info("Bot initialized and starting main loop.")

try:
    while True:
        start_loop = time.time()
        try:
            now = datetime.now()
            start_dt = now - timedelta(minutes=history_minutes)
            # Fetch minute-level data
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
            logger.info(f"Signals at {now}: {signals}")
            # Execute signals
            executed = executor.execute_signals(df)
            # Update risk manager
            for sym, trade in executed.items():
                if trade:
                    price = getattr(trade.orderStatus, 'avgFillPrice', None) or trade.orderStatus.lastFillPrice
                    risk_manager.record_trade(sym, trade.order.action, price)
                    logger.info(f"Executed {trade.order.action} {sym} @ {price}")
            # Log risk metrics
            metrics = risk_manager.metrics()
            logger.info(f"Drawdown: {metrics['drawdown']:.2%}, Max Drawdown: {metrics['max_drawdown']:.2%}")

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            for attempt in range(1, max_retries+1):
                try:
                    logger.info(f"Attempting reconnect ({attempt}/{max_retries})...")
                    executor.disconnect()
                    executor, predictor, risk_manager = init_components()
                    logger.info("Reconnected and reinitialized components.")
                    break
                except Exception as err:
                    logger.error(f"Reconnect attempt failed: {err}")
                    time.sleep(retry_delay)
            else:
                logger.critical("Max retries exceeded, stopping bot.")
                break

        # Sleep respecting interval timing
        elapsed = time.time() - start_loop
        sleep_time = max(0, interval_seconds - elapsed)
        time.sleep(sleep_time)

except KeyboardInterrupt:
    logger.info("KeyboardInterrupt received, stopping bot...")

finally:
    executor.disconnect()
    # Export final report
    report_path = 'reports/risk_report.html'
    risk_manager.generate_report(report_path)
    logger.info(f"Clean disconnection. Risk report saved to {report_path}.")
```
