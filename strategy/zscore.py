import statistics
from collections import deque


class RollingZScore:
    def __init__(self, window=10):
        self.window = window
        self._prices = deque(maxlen=window)

    def update(self, price):
        # feed one bar's price in; returns how many std devs the current price
        # is from the rolling mean, or None while the window isn't full yet
        # (or the window has zero variance, where a z-score is undefined).
        self._prices.append(price)
        if len(self._prices) < self.window:
            return None

        mean = statistics.mean(self._prices)
        std = statistics.stdev(self._prices)  # sample std dev (ddof=1), matches pandas' rolling().std() default
        if std == 0:
            return None

        return (price - mean) / std
