class Trade:
    # One completed round-trip: entry fill through exit fill. Built by
    # Portfolio when a position fully closes - this is what's needed to
    # compute win rate / average PnL per trade without manually reconstructing
    # trades from a flat list of fills.
    def __init__(self, market_id, quantity,
                 entry_time, entry_price, entry_fee,
                 exit_time, exit_price, exit_fee):
        self.market_id = market_id
        self.quantity = quantity
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.entry_fee = entry_fee
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.exit_fee = exit_fee

    @property
    def gross_pnl(self):
        return (self.exit_price - self.entry_price) * self.quantity

    @property
    def net_pnl(self):
        return self.gross_pnl - self.entry_fee - self.exit_fee
