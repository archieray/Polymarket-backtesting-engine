from dataclasses import dataclass
from datetime import datetime

class Event:
    pass


# New market data event
@dataclass
class MarketEvent(Event):
    timestamp: datetime
    market_id: str
    price: float
    liquidity: float
    



# Sends a signal from the trading strategy
@dataclass
class SignalEvent(Event):
    timestamp: datetime
    market_id: str
    direction: str # YES/NO
    strength: float = 1.0 # confidence


#Event of sending order the the execution system
@dataclass
class OrderEvent(Event):
    timestamp: datetime
    market_id: str
    direction: str
    order_type: str # Market, or limit order
    quantity: float

# Confirmation of the traede
@dataclass
class FillEvent(Event):
    timestamp: datetime
    market_id: str
    direction: str
    quantity: float
    fee: float
