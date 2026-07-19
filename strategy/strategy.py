from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def calculate_signals(self, event):
        # event: a MarketEvent (Events/event.py) - one bar at a time.
        # returns: a SignalEvent (Events/event.py) if the rule fires on this
        # bar, otherwise None.
        raise NotImplementedError
