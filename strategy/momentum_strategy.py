from Events.event import SignalEvent
from strategy.sma import SimpleMovingAverage
from strategy.strategy import Strategy


class SMAMomentumStrategy(Strategy):
    # Trend-following: go long when price crosses above its own moving
    # average (trending up), exit when it crosses back below. This is a
    # crossover proxy for momentum, not a literal rate-of-change calculation -
    # it answers "is price above trend right now", not "how fast is it moving".
    #
    # NOTE: assumes it only ever sees events for one market - it keeps a
    # single SMA and a single position flag, with no per-symbol keying. Feeding
    # it two different markets' events would silently blend their prices.
    def __init__(self, window=10):
        self.sma = SimpleMovingAverage(window=window)
        self._prev_above = None  # None until the SMA has a first value to compare against
        self._in_position = False

    def calculate_signals(self, event):
        sma_value = self.sma.update(event.price)
        if sma_value is None:
            # not enough bars yet for the SMA to have a value
            return None

        above = event.price > sma_value
        signal = None

        # Only fire on the actual crossing bar (a transition), not on every
        # bar spent above/below the average - that's what self._prev_above is
        # for. self._in_position guards against re-firing the same signal
        # while already in that state.
        if self._prev_above is not None:
            if above and not self._prev_above and not self._in_position:
                signal = SignalEvent(event.timestamp, event.market_id, "YES")
                self._in_position = True
            elif not above and self._prev_above and self._in_position:
                signal = SignalEvent(event.timestamp, event.market_id, "NO")
                self._in_position = False

        self._prev_above = above
        return signal
