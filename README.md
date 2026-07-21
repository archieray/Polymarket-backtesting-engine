# Polymarket Backtesting Engine

An event-driven backtester for Polymarket prediction markets, built for **Warwick Quant Soc's Polymarket trading team** to test trading strategies against real market data before running them live.

Unlike most public backtesting tools (which tend to only cover crypto up/down markets), this is meant to work against **any** Polymarket market — you just need that market's token ID (see below).

## Setup

- **Python 3.9+**
- Two third-party packages, nothing else:
  ```
  pip install pandas requests
  ```

That's the whole setup. **This is fully self-contained** — no API keys, no accounts, no database, no server to run. Clone the repo, install those two packages, and you're ready. All data comes from Polymarket's public Gamma and CLOB APIs, which need no authentication.

## Before you start: you need market token IDs

A Polymarket "event" (e.g. *"How many 7.0+ earthquakes in 2026?"*) is usually split into several separate binary YES/NO **markets** (e.g. one per outcome bin), each with its own token ID. To backtest a specific market, you need that market's token ID.

To find one:

1. Get the event's slug from its Polymarket URL — `polymarket.com/event/<slug>`.
2. Query the Gamma API: `https://gamma-api.polymarket.com/events?slug=<slug>`.
3. In the response, find the market you want inside `"markets"`, and read its `clobTokenIds` field — it's a list of two token IDs; the first is the YES token (what this engine trades).

`scripts/fetch_earthquake_market.py` is a worked example of this pattern end to end (fetch by token ID → save as CSV). Copy it and swap in a different token ID / output filename to pull a new market.

## Quickstart

```python
import queue
from data_handler.data_handler import HistoricCSVDataHandler
from strategy.momentum_strategy import SMAMomentumStrategy
from execution.execution import NaiveExecutionHandler
from portfolio.portfolio import Portfolio
from performance.performance import Performance
from backtest import Backtest

q = queue.Queue()
dh = HistoricCSVDataHandler(q, "data", ["earthquakes_14_16"])   # {csv_dir}/{symbol}.csv
strategy = SMAMomentumStrategy(window=10)
portfolio = Portfolio(q, initial_cash=10000.0, quantity_per_trade=100.0)
execution = NaiveExecutionHandler(q, dh, fee_rate=0.05)          # see fee rates below

bt = Backtest(q, dh, strategy, portfolio, execution)
bt.run()

print(Performance(portfolio, initial_cash=10000.0).summary())
```

## Features

- **Data handling** — `data_handler/data_handler.py`: streams a CSV of historic prices bar by bar, one independent stream per market symbol (no lookahead — a strategy only ever sees bars up to "now").
- **Strategies** — pluggable via a `Strategy` base class (`strategy/strategy.py`):
  - `SMAMomentumStrategy` — SMA crossover, long on cross-above, exit on cross-below.
  - `MeanReversionStrategy` — rolling z-score, long when oversold, exit on reversion to the mean.
  - Both long-only (no shorting).
- **Execution simulation** — `execution/execution.py`: fills market orders at the current bar's price. Fees are computed from Polymarket's real category-based fee schedule (`execution/fee_rates.py`), auto-resolved per market via its Gamma API tags — so a Politics market and a Crypto market are charged correctly, not a flat guess.
- **Portfolio** — `portfolio/`: cash, position (weighted-average cost basis), and completed-trade bookkeeping; long-only; fixed quantity per trade; automatically force-closes any open position at the last known price once a backtest's data runs out (so results aren't distorted by an unresolved open position).
- **Performance** — `performance/performance.py`: total return %, number of trades, win rate, average win/loss size.
- **Alerts** — the Portfolio flags anomalies (e.g. a close request larger than the position actually held) rather than silently clamping them without a trace.

## Writing your own strategy

Subclass `Strategy` (`strategy/strategy.py`) and implement one method:

```python
def calculate_signals(self, event) -> SignalEvent | None:
    ...
```

`event` is a `MarketEvent` (`.timestamp`, `.market_id`, `.price`). Return a `SignalEvent(event.timestamp, event.market_id, "YES")` to enter, `"NO"` to exit, or `None` to do nothing on that bar. Use `strategy/momentum_strategy.py` or `strategy/mean_reversion_strategy.py` as a template — they're both under 50 lines.

This requires **low-to-mid level Python** (writing a class, basic control flow, comfort reading pandas/rolling-window style logic) — it's a coding tool, not a no-code strategy builder.

## Things to know before you trust a result

- Fills happen **instantly at the current bar's price** — no slippage, no order-book depth, no next-bar delay. This is a deliberate first-pass simplification, not an oversight; real fills would be worse than what you'll see here, especially in thin markets.
- Every trade uses a **fixed quantity** — no position sizing based on signal strength or confidence yet.
- No stop-loss / take-profit overlay yet — a strategy only exits when its own rule says to.
- Data is **CSV snapshots**, pulled on demand — there's no live/streaming feed.
- Treat any backtest result as a directional signal about a strategy, not a validated live-trading edge — always sanity-check on multiple markets and time periods before trusting a number.

See `backlog.md` for a running list of ideas not yet built.
