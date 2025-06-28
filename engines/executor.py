import logging
from datetime import datetime

from ib_insync import IB, Stock, MarketOrder, Order, Trade

from core.database import Database
from ai.predictor import AIPredictor

# Configure logging
type=logging.INFO)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Executor:
    """
    Live order executor using IBKR via ib_insync,
    with trade logging and AI-based signal integration.
    """
    def __init__(
        self,
        tickers,
        host: str = '127.0.0.1',
        port: int = 7497,
        clientId: int = 1,
        db_url: str = 'postgresql://user:pass@db-host:5432/botdb',
    ):
        # Connect to IBKR
        self.ib = IB()
        self.ib.connect(host, port, clientId)
        logger.info(f"Connected to IBKR at {host}:{port} (clientId={clientId})")

        # Initialize database
        self.db = Database(db_url)

        # Initialize AI predictor
        self.predictor = AIPredictor(tickers)
        self.predictor.train_finrl_agent()
        self.predictor.train_qlib_strategy()
        logger.info("AI Predictor initialized and trained.")

    def create_contract(self, symbol: str, currency: str = 'USD', exchange: str = 'SMART') -> Stock:
        """
        Create and return an IBKR stock contract.
        """
        return Stock(symbol, exchange, currency)

    def place_market_order(self, symbol: str, quantity: float) -> Trade:
        """
        Place a market BUY or SELL order for given symbol and quantity.
        Logs trade to the database.
        """
        contract = self.create_contract(symbol)
        action = 'BUY' if quantity > 0 else 'SELL'
        order = MarketOrder(action, abs(quantity))
        trade = self.ib.placeOrder(contract, order)
        self.ib.sleep(1)

        logger.info(f"Market order placed: {action} {quantity} {symbol}")
        self.db.log_trade(trade)
        return trade

    def place_trailing_stop(
        self,
        symbol: str,
        quantity: float,
        trailPercent: float
    ) -> Trade:
        """
        Place a trailing stop order.
        """
        contract = self.create_contract(symbol)
        order = Order()
        order.action = 'SELL' if quantity > 0 else 'BUY'
        order.orderType = 'TRAIL'
        order.totalQuantity = abs(quantity)
        order.trailType = 1  # percent
        order.trailPercent = trailPercent * 100

        trade = self.ib.placeOrder(contract, order)
        self.ib.sleep(1)

        logger.info(
            f"Trailing stop placed: {order.action} {quantity} {symbol} @ trail {trailPercent:.2%}"
        )
        self.db.log_trade(trade)
        return trade

    def execute_signals(self, current_data) -> dict:
        """
        Generate signals via AI predictor and execute orders accordingly.
        Returns executed orders mapping.
        """
        signals = self.predictor.predict_signals(current_data)
        executed = {}

        for sym, signal in signals.items():
            if signal == 'buy':
                trade = self.place_market_order(sym, 100)  # adjust quantity logic as needed
                executed[sym] = trade
            elif signal == 'sell':
                trade = self.place_market_order(sym, -100)
                executed[sym] = trade
            else:
                executed[sym] = None

        return executed

    def cancel_all(self) -> None:
        """
        Cancel all open orders.
        """
        orders = self.ib.openOrders()
        for o in orders:
            self.ib.cancelOrder(o)
        logger.info(f"Cancelled {len(orders)} open orders")

    def disconnect(self) -> None:
        """
        Disconnect from IBKR and close database session.
        """
        self.db.close()
        self.ib.disconnect()
        logger.info("Disconnected from IBKR and closed database connection.")
