import pandas as pd
import yfinance as yf
import os
from datetime import datetime
from finrl import config, create_environment, DRLAgent
from finrl.finrl_meta.data_processors.processor_yahoodownloader import YahooDownloader
import qlib
from qlib.config import REG_US
from qlib.data import D
from qlib.contrib.strategy import TopkDropoutStrategy

class AIPredictor:
    """
    AI Predictor combining FinRL (Reinforcement Learning) and Qlib (Machine Learning).
    """

    def __init__(self, ticker_list, start_date="2020-01-01", end_date=None):
        self.tickers = ticker_list
        self.start = start_date
        self.end = end_date or datetime.today().strftime("%Y-%m-%d")
        # Initialize Qlib for US market
        qlib.init(provider_uri='~/.qlib/qlib_data/US', region=REG_US)
        # Placeholders
        self.finrl_agent = None
        self.qlib_strategy = None

    def train_finrl_agent(self):
        """Train a DQN agent using FinRL."""
        df = YahooDownloader(start_date=self.start,
                             end_date=self.end,
                             ticker_list=self.tickers).fetch_data()
        env = create_environment(df)
        agent = DRLAgent(env=env)
        self.finrl_agent = agent.get_model("dqn")
        self.finrl_agent.train()

    def train_qlib_strategy(self):
        """Configure and initialize a Qlib strategy."""
        self.qlib_strategy = TopkDropoutStrategy(topk=10, n_drop=0, signal="score")

    def predict_signals(self, current_data):
        """
        Generate buy/sell/hold signals.
        current_data: pandas DataFrame indexed by datetime, columns multiindex for tickers and OHLCV.
        Returns: dict {ticker: signal}.
        """
        signals = {}
        # FinRL prediction
        if self.finrl_agent:
            frl_signals = self.finrl_agent.DRL_prediction(current_data)
        else:
            frl_signals = {t: "hold" for t in self.tickers}

        # Qlib prediction (using generated signals)
        if self.qlib_strategy:
            q_data = D.features(self.tickers, ['$close', '$volume'], self.start, self.end)
            q_signals = self.qlib_strategy.generate_signals(q_data)
        else:
            q_signals = pd.Series({t: 0 for t in self.tickers})

        # Ensemble logic
        for t in self.tickers:
            frl = frl_signals.get(t, "hold")
            qlb = "buy" if q_signals.get(t, 0) > 0 else ("sell" if q_signals.get(t, 0) < 0 else "hold")
            signals[t] = frl if frl == qlb else "hold"
        return signals
