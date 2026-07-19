from Events.event import SignalEvent
from strategy.sma import SimpleMovingAverage
from strategy.strategy import Strategy


class SMAMomentumStrategy(Strategy):
    def __init__(self, window=10):
        self.sma = SimpleMovingAverage(window=window)
        self._prev_above = None  # None until the SMA has a first value to compare against
        self._in_position = False

    def calculate_signals(self, event):
        sma_value = self.sma.update(event.price)
        if sma_value is None:
            return None

        above = event.price > sma_value
        signal = None

        if self._prev_above is not None:
            if above and not self._prev_above and not self._in_position:
                signal = SignalEvent(event.timestamp, event.market_id, "YES")
                self._in_position = True
            elif not above and self._prev_above and self._in_position:
                signal = SignalEvent(event.timestamp, event.market_id, "NO")
                self._in_position = False

        self._prev_above = above
        return signal
