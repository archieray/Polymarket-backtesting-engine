from Events.event import OrderEvent
from portfolio.order import Order
from portfolio.position import Position
from portfolio.trade import Trade


class Portfolio:
    def __init__(self, events_queue, initial_cash=10000.0, quantity_per_trade=100.0):
        self.events_queue = events_queue
        self.cash = initial_cash
        self.quantity_per_trade = quantity_per_trade

        self.positions = {}  # market_id -> Position
        self.orders = {}  # market_id -> Order (at most one live order per symbol)
        self.trades = []  # completed round-trips
        self._pending_entry = {}  # market_id -> entry fill info, while a position is open
        self.equity_curve = []  # list of (timestamp, equity)
        self.alerts = []  # notable events (e.g. capped closes) - surfaced to a future frontend

    def process_signal(self, event):
        # "YES" enters (buy), "NO" exits (sell the existing position) - both
        # trade the same fixed quantity_per_trade, no sizing logic yet.
        order_event = OrderEvent(
            timestamp=event.timestamp,
            market_id=event.market_id,
            direction=event.direction,
            order_type="MARKET",
            quantity=self.quantity_per_trade,
        )
        self.orders[event.market_id] = Order(order_event)
        self.events_queue.put(order_event)

    def process_fill(self, event):
        order = self.orders.get(event.market_id)
        if order is not None:
            order.mark_filled(event)

        position = self.positions.setdefault(event.market_id, Position(event.market_id))

        quantity_delta = event.quantity if event.direction == "YES" else -event.quantity
        opened, closed, realized_pnl = position.update(quantity_delta, event.fill_price)

        if quantity_delta < 0 and closed < -quantity_delta:
            self._flag_capped_close(event, requested=-quantity_delta, closed=closed)

        if opened:
            self.cash -= opened * event.fill_price + event.fee
            self._pending_entry[event.market_id] = {
                "time": event.timestamp,
                "price": event.fill_price,
                "fee": event.fee,
            }

        if closed:
            self.cash += closed * event.fill_price - event.fee

            if position.quantity == 0:
                entry = self._pending_entry.pop(event.market_id, None)
                if entry is not None:
                    self.trades.append(Trade(
                        market_id=event.market_id,
                        quantity=closed,
                        entry_time=entry["time"],
                        entry_price=entry["price"],
                        entry_fee=entry["fee"],
                        exit_time=event.timestamp,
                        exit_price=event.fill_price,
                        exit_fee=event.fee,
                    ))

    def _flag_capped_close(self, event, requested, closed):
        # A close request exceeded what was actually held, so Position
        # silently capped it - flag it here instead so it's not lost. Every
        # occurrence is logged now; once a frontend exists, self.alerts is
        # what it would read from.
        alert = {
            "type": "capped_close",
            "timestamp": event.timestamp,
            "market_id": event.market_id,
            "requested": requested,
            "closed": closed,
            "shortfall": requested - closed,
        }
        self.alerts.append(alert)
        print(
            f"ALERT: close request for {event.market_id} at {event.timestamp} was capped - "
            f"requested {requested}, closed {closed} (shortfall {alert['shortfall']})"
        )

    def update_timeindex(self, event):
        position = self.positions.get(event.market_id)
        if position is not None:
            position.last_price = event.price

        equity = self.cash + sum(
            pos.quantity * pos.last_price
            for pos in self.positions.values()
            if pos.last_price is not None
        )
        self.equity_curve.append((event.timestamp, equity))

    def get_equity_curve(self):
        return self.equity_curve
