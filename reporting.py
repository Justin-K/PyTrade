# A report generation system
from trade import Trade


class Report:

    def __init__(self):
        self._trades = []

    def addTrade(self, trade: Trade):
        self._trades.append(trade)

