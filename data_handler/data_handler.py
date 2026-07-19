from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from Events.event import MarketEvent


class DataHandler(ABC):
    # Any backend (CSV today, SQLite/live API later) implements just these two
    # methods, so nothing downstream needs to know which backend it's talking to.
    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        raise NotImplementedError

    @abstractmethod
    def update_bars(self):
        raise NotImplementedError


class HistoricCSVDataHandler(DataHandler):
    def __init__(self, events_queue, csv_dir, symbol_list):
        self.events_queue = events_queue
        self.csv_dir = Path(csv_dir)
        self.symbol_list = symbol_list
        self.continue_backtest = True

        # symbol_data: one lazy row-iterator per symbol, consumed as the backtest
        # advances (single pass, no reset).
        # latest_symbol_data: bars already streamed per symbol - get_latest_bars
        # reads only from here, so a strategy/indicator can never see future bars.
        self.symbol_data = {}
        self.latest_symbol_data = {}

        self._load_csv_data()

    def _load_csv_data(self):
        for symbol in self.symbol_list:
            df = pd.read_csv(
                self.csv_dir / f"{symbol}.csv",
                # index_col=0 drops the stray unnamed index column pandas wrote
                # when the fetch script did df.to_csv(...).
                index_col=0,
                parse_dates=["time"],
            )
            df = df.sort_values("time").reset_index(drop=True)
            self.symbol_data[symbol] = df.itertuples(index=False)
            self.latest_symbol_data[symbol] = []

    def get_latest_bars(self, symbol, N=1):
        # last N bars seen so far - the lookback window strategies/indicators query.
        return self.latest_symbol_data[symbol][-N:]

    def update_bars(self):
        # Called once per tick: pulls the next row for every symbol still active
        # and emits one MarketEvent per symbol onto the shared queue. Symbols
        # exhaust independently - the backtest only ends once all of them have.
        for symbol in list(self.symbol_data.keys()):
            try:
                bar = next(self.symbol_data[symbol])
            except StopIteration:
                del self.symbol_data[symbol]
                if not self.symbol_data:
                    self.continue_backtest = False
                continue

            self.latest_symbol_data[symbol].append(bar)
            self.events_queue.put(MarketEvent(
                timestamp=bar.time,
                # friendly symbol, not the raw token id, so it matches how
                # get_latest_bars/latest_symbol_data are keyed downstream.
                market_id=symbol,
                price=bar.prices,
                # placeholder: this data source has no order-book/liquidity info yet.
                liquidity=float("nan"),
            ))
