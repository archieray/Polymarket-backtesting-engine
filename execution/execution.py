from abc import ABC, abstractmethod

from Events.event import FillEvent


class ExecutionHandler(ABC):
    @abstractmethod
    def execute_order(self, event):
        # event: an OrderEvent (Events/event.py).
        # pushes a FillEvent onto the shared events_queue once executed.
        raise NotImplementedError


class NaiveExecutionHandler(ExecutionHandler):
    # Fills a Market order at the current/most-recent bar's price for that
    # market - no slippage, no next-bar delay. This is the user's flagged
    # "wrong approach on purpose" first pass; revisit once execution realism
    # (order book depth, next-bar fills) matters.
    def __init__(self, events_queue, data_handler, fee_rate=0.05):
        self.events_queue = events_queue
        self.data_handler = data_handler
        self.fee_rate = fee_rate

    def execute_order(self, event):
        if event.order_type != "MARKET":
            # no limit-order logic exists yet - fail loudly rather than
            # silently mis-filling one as if it were a market order.
            raise NotImplementedError(f"unsupported order_type: {event.order_type}")

        latest_bar = self.data_handler.get_latest_bars(event.market_id, N=1)[-1]
        fill_price = latest_bar.prices

        # fee = C x feeRate x p x (1-p): peaks at 50c (max uncertainty),
        # approaches 0 near the edges (0c or $1). Applies identically to
        # entries and exits since both are just OrderEvents through this path.
        fee = event.quantity * self.fee_rate * fill_price * (1 - fill_price)

        self.events_queue.put(FillEvent(
            timestamp=event.timestamp,
            market_id=event.market_id,
            direction=event.direction,
            quantity=event.quantity,
            fill_price=fill_price,
            fee=fee,
        ))
