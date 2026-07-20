class Position:
    # Long-only: quantity is always >= 0. Both strategies only ever go long
    # YES then flatten, never invert to short - no short-selling support here.
    def __init__(self, market_id):
        self.market_id = market_id
        self.quantity = 0.0
        self.avg_price = 0.0
        self.last_price = None  # most recent mark price, for equity calc

    def update(self, quantity_delta, price):
        # returns (opened, closed, realized_pnl). A positive delta opens/adds
        # to the position (weighted-average cost basis); a negative delta
        # closes up to the current quantity, realizing PnL on the closed part.
        if quantity_delta > 0:
            new_quantity = self.quantity + quantity_delta
            self.avg_price = (
                (self.quantity * self.avg_price) + (quantity_delta * price)
            ) / new_quantity
            self.quantity = new_quantity
            return quantity_delta, 0.0, 0.0

        elif quantity_delta < 0:
            closed = min(-quantity_delta, self.quantity)
            realized_pnl = closed * (price - self.avg_price)
            self.quantity -= closed
            if self.quantity == 0:
                self.avg_price = 0.0
            return 0.0, closed, realized_pnl

        return 0.0, 0.0, 0.0
