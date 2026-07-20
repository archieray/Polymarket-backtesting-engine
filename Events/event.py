from dataclasses import dataclass
from datetime import datetime

# Base marker class - everything passed through the event pipeline is one of
# these, so a queue/engine can handle them generically before dispatching by
# concrete type (MarketEvent, SignalEvent, OrderEvent, FillEvent below).
class Event:
    pass


# One bar of price data for a market. Emitted by a DataHandler
# (data_handler/data_handler.py) as it steps through history.
@dataclass
class MarketEvent(Event):
    timestamp: datetime
    market_id: str
    price: float
    liquidity: float  # currently always NaN - no order-book data source yet


# A trading decision from a Strategy (strategy/strategy.py), in response to a
# MarketEvent. Not an order yet - just "I want to be long/flat here."
@dataclass
class SignalEvent(Event):
    timestamp: datetime
    market_id: str
    direction: str  # "YES" to enter a long, "NO" to exit it (not "buy NO")
    strength: float = 1.0  # confidence/sizing hint - unused until Portfolio exists


# A concrete instruction to the execution system, generated from a SignalEvent
# (e.g. by a future Portfolio) once position sizing is decided.
@dataclass
class OrderEvent(Event):
    timestamp: datetime
    market_id: str
    direction: str
    order_type: str  # "MARKET" or "LIMIT"
    quantity: float

# Confirmation that an OrderEvent was executed, produced by an execution handler.
@dataclass
class FillEvent(Event):
    timestamp: datetime
    market_id: str
    direction: str
    quantity: float
    fill_price: float
    fee: float
