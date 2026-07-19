from Events.event import SignalEvent
from strategy.strategy import Strategy
from strategy.zscore import RollingZScore


class MeanReversionStrategy(Strategy):
    def __init__(self, window=10, entry_threshold=-2.0):
        self.zscore = RollingZScore(window=window)
        self.entry_threshold = entry_threshold
        self._in_position = False

    def calculate_signals(self, event):
        z = self.zscore.update(event.price)
        if z is None:
            return None

        signal = None
        if not self._in_position and z < self.entry_threshold:
            # oversold: price has strayed far enough below the mean to bet on reversion up
            signal = SignalEvent(event.timestamp, event.market_id, "YES")
            self._in_position = True
        elif self._in_position and z >= 0.0:
            # reverted back to neutral - close the position
            signal = SignalEvent(event.timestamp, event.market_id, "NO")
            self._in_position = False

        return signal
