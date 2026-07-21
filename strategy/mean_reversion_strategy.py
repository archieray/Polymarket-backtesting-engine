from Events.event import SignalEvent
from strategy.strategy import Strategy
from strategy.zscore import RollingZScore


class MeanReversionStrategy(Strategy):
    # Long-only mean reversion: enter when price has strayed entry_threshold
    # std devs below its rolling mean (oversold, bet on reverting up), exit
    # once it's back to the mean (z >= 0). Doesn't trade the overbought side.
    #
    # NOTE: same single-market assumption as SMAMomentumStrategy - one
    # RollingZScore and one position flag, no per-symbol keying.
    def __init__(self, window=10, entry_threshold=-2.0):
        super().__init__()
        self.zscore = RollingZScore(window=window)
        self.entry_threshold = entry_threshold

    def calculate_signals(self, event):
        z = self.zscore.update(event.price)
        if z is None:
            return None

        signal = None
        if not self._in_position and z < self.entry_threshold:
            # oversold: price has strayed far enough below the mean to bet on reversion up
            signal = SignalEvent(event.timestamp, event.market_id, "YES")
            self._enter()
        elif self._in_position and z >= 0.0:
            # reverted back to neutral - close the position
            signal = SignalEvent(event.timestamp, event.market_id, "NO")
            self._exit()

        return signal
