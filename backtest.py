import time

from Events.event import FillEvent, MarketEvent, OrderEvent, SignalEvent


class Backtest:
    # Owns the event queue and drives the main loop: pulls bars from
    # data_handler, dispatches each event on the queue to whichever component
    # handles that type, until the data runs out. Every component here is
    # constructor-injected and must already share the same events_queue -
    # this class doesn't create it or wire it into the components itself.
    def __init__(self, events_queue, data_handler, strategy, portfolio, execution_handler, verbose=True):
        self.events_queue = events_queue
        self.data_handler = data_handler
        self.strategy = strategy
        self.portfolio = portfolio
        self.execution_handler = execution_handler
        self.verbose = verbose

        self.events_processed = 0
        self._last_market_event = None

    def run(self):
        if self.verbose:
            print("Starting backtest...")
        start_time = time.time()

        while self.data_handler.continue_backtest:
            self.data_handler.update_bars()
            self._process_events()

        # data's exhausted - if the strategy is still holding a position,
        # mark it out at the last known price rather than dropping it silently.
        if self._last_market_event is not None:
            close_signal = self.strategy.force_close(self._last_market_event)
            if close_signal is not None:
                self.events_queue.put(close_signal)
                self._process_events()

        elapsed = time.time() - start_time
        if self.verbose:
            print(f"Backtest completed in {elapsed:.2f} seconds.")
            print(f"Total events processed: {self.events_processed}")

    def _process_events(self):
        while not self.events_queue.empty():
            event = self.events_queue.get()
            self.events_processed += 1

            if isinstance(event, MarketEvent):
                self._last_market_event = event
                signal = self.strategy.calculate_signals(event)
                if signal is not None:
                    self.events_queue.put(signal)
                self.portfolio.update_timeindex(event)

            elif isinstance(event, SignalEvent):
                self.portfolio.process_signal(event)

            elif isinstance(event, OrderEvent):
                self.execution_handler.execute_order(event)

            elif isinstance(event, FillEvent):
                self.portfolio.process_fill(event)

    def get_results(self):
        return self.portfolio.get_equity_curve()
