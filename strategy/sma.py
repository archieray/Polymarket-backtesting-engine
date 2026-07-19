from collections import deque


class SimpleMovingAverage:
    def __init__(self, window=10):
        self.window = window
        self._prices = deque(maxlen=window)

    def update(self, price):
        # feed one bar's price in; returns the rolling average once the window
        # has filled, or None while there aren't yet enough bars to average.
        self._prices.append(price)
        if len(self._prices) < self.window:
            return None
        return sum(self._prices) / self.window
