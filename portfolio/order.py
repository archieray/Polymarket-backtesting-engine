class Order:
    # Thin wrapper around an OrderEvent (Events/event.py). Intentionally
    # minimal - our naive execution model fills every order instantly in the
    # same tick, so there's no multi-bar pending lifecycle to track (unlike
    # backtrader's Order, which persists across bars for limit/stop types).
    # Kept as its own class as groundwork in case limit orders get added later.
    def __init__(self, event):
        self.market_id = event.market_id
        self.direction = event.direction
        self.order_type = event.order_type
        self.quantity = event.quantity
        self.timestamp = event.timestamp
        self.status = "CREATED"
        self.fill_price = None
        self.fee = None

    def mark_filled(self, fill_event):
        self.status = "FILLED"
        self.fill_price = fill_event.fill_price
        self.fee = fill_event.fee
