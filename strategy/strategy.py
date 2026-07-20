from abc import ABC, abstractmethod

from Events.event import SignalEvent


class Strategy(ABC):
    @abstractmethod
    def calculate_signals(self, event):
        # event: a MarketEvent (Events/event.py) - one bar at a time.
        # returns: a SignalEvent (Events/event.py) if the rule fires on this
        # bar, otherwise None.
        raise NotImplementedError

    def force_close(self, event):
        # Called once when the data stream ends, so a position left open at
        # the last bar isn't just silently dropped. Marks out at event.price
        # (the last available price), not a true market resolution.
        if not self._in_position:
            return None
        self._in_position = False
        return SignalEvent(event.timestamp, event.market_id, "NO")
