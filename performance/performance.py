class Performance:
    # Summarizes a completed backtest's results. No abstract base class here -
    # unlike DataHandler/ExecutionHandler/Strategy, there's only one thing this
    # does and no alternate implementation is anticipated yet.
    def __init__(self, portfolio, initial_cash):
        self.portfolio = portfolio
        self.initial_cash = initial_cash

    def summary(self):
        trades = self.portfolio.trades
        equity_curve = self.portfolio.equity_curve
        final_equity = equity_curve[-1][1] if equity_curve else self.initial_cash

        total_return_pct = (final_equity - self.initial_cash) / self.initial_cash * 100

        wins = [t for t in trades if t.net_pnl > 0]
        losses = [t for t in trades if t.net_pnl <= 0]
        num_trades = len(trades)

        return {
            "total_return_pct": total_return_pct,
            "final_equity": final_equity,
            "num_trades": num_trades,
            "win_rate_pct": (len(wins) / num_trades * 100) if num_trades else 0.0,
            "avg_win": (sum(t.net_pnl for t in wins) / len(wins)) if wins else 0.0,
            "avg_loss": (sum(t.net_pnl for t in losses) / len(losses)) if losses else 0.0,
        }
