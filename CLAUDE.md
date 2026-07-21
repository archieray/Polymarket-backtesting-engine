# PolyBacktestingEngine — project summary

## What this is

A hand-built, event-driven backtesting engine for Polymarket prediction markets, developed incrementally (one small file at a time) against a single real market: "How many 7.0+ earthquakes in 2026?" (the 14-16 outcome bin). Motivated by existing tools (e.g. polybacktest.com) only covering crypto up/down markets — this is meant to be general-purpose across any Polymarket market, though only one market has been tested so far.

## Rules

- Update ROADMAP.md everytime i tell you i am going to push

## Architecture (built so far)

```
data_handler/data_handler.py   # HistoricCSVDataHandler - reads CSV, streams MarketEvents
strategy/sma.py                # SimpleMovingAverage indicator
strategy/zscore.py             # RollingZScore indicator
strategy/strategy.py           # Strategy ABC + shared force_close() for end-of-backtest
strategy/momentum_strategy.py  # SMAMomentumStrategy - SMA crossover, long/exit
strategy/mean_reversion_strategy.py  # MeanReversionStrategy - z-score based, long-only
execution/execution.py         # NaiveExecutionHandler - fills Market orders at current bar's price
portfolio/position.py          # Position - long-only quantity/avg_price tracking
portfolio/order.py             # Order - thin wrapper around OrderEvent
portfolio/trade.py             # Trade - one completed entry->exit round-trip, gross/net PnL
portfolio/portfolio.py         # Portfolio - cash, positions, signal->order->fill bookkeeping, equity curve
backtest.py                    # Backtest - owns the event queue, drives the main loop
Events/event.py                # MarketEvent, SignalEvent, OrderEvent, FillEvent dataclasses
scripts/fetch_earthquake_market.py  # one-off CSV fetch from Polymarket's public CLOB API
data/earthquakes_14_16.csv     # 1,437 bars, 30-min fidelity
ROADMAP.md                     # Mermaid diagram of the pipeline + backlog
backlog.md                     # user's own running notes on deferred ideas
```

Full event flow: `MarketEvent -> Strategy.calculate_signals -> SignalEvent -> Portfolio.process_signal -> OrderEvent -> ExecutionHandler.execute_order -> FillEvent -> Portfolio.process_fill (updates Position, cash, Trade, equity_curve)`. Verified end-to-end against the real CSV: 2,313 events processed, 146 trades, cash reconciles exactly against initial_cash + sum(trade.net_pnl).