from core.database import Database
...
from ai.predictor import AIPredictor
predictor = AIPredictor(["SNDL","NOK"])
predictor.train_finrl_agent()
predictor.train_qlib_strategy()
signals = predictor.predict_signals(current_data)
print(signals)

class Executor:
    def __init__(self, host='127.0.0.1', port=7497, clientId=1):
        ...
        # initialize DB
        self.db = Database()
...
    def place_market_order(...):
        ...
        self.db.log_trade(trade)
        return trade
...
    def disconnect(self):
        self.db.close()
        self.ib.disconnect()

from ib_insync import IB, Stock, MarketOrder, Order
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Executor:
    """
    Live order executor using IBKR via ib_insync.
    """
    def __init__(self, host='127.0.0.1', port=7497, clientId=1):
        self.ib = IB()
        self.ib.connect(host, port, clientId)
        logger.info(f"Connected to IBKR at {host}:{port} (clientId={clientId})")

    def create_contract(self, symbol: str, currency: str = 'USD', exchange: str = 'SMART') -> Stock:
        """
        Create and return an IB stock contract.
        """
        contract = Stock(symbol, exchange, currency)
        return contract

    def place_market_order(self, symbol: str, quantity: float):
        """
        Place a market order for the given symbol and quantity.
        """
        contract = self.create_contract(symbol)
        order = MarketOrder('BUY' if quantity > 0 else 'SELL', abs(quantity))
        trade = self.ib.placeOrder(contract, order)
        self.ib.sleep(1)  # give IB time to process
        logger.info(f"Market order placed: {order.action} {quantity} {symbol}")
        return trade

    def place_trailing_stop(self, symbol: str, quantity: float, trailPercent: float):
        """
        Place a trailing stop order.
        """
        contract = self.create_contract(symbol)
        order = Order()
        order.action = 'SELL' if quantity > 0 else 'BUY'
        order.orderType = 'TRAIL'
        order.totalQuantity = abs(quantity)
        order.trailType = 1  # percent
        order.trailPercent = trailPercent * 100  # e.g. 0.015 -> 1.5%
        trade = self.ib.placeOrder(contract, order)
        self.ib.sleep(1)
        logger.info(f"Trailing stop placed: {order.action} {quantity} {symbol} @ trail {trailPercent:.2%}")
        return trade

    def cancel_all(self):
        """
        Cancel all open orders.
        """
        orders = self.ib.openOrders()
        for o in orders:
            self.ib.cancelOrder(o)
        logger.info(f"Cancelled {len(orders)} open orders")

    def disconnect(self):
        """
        Disconnect IB session.
        """
        self.ib.disconnect()
        logger.info("Disconnected from IBKR")
feat: add IBKR live execution module (executor.py)
