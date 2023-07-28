from function_library import seperatePair
from dataclasses import dataclass


class Market:

    def __init__(self, symbol: str):
        self.market_str = symbol.upper()
        self.base_asset, self.quote_asset = seperatePair(self.market_str)


@dataclass(init=True)
class AssociatedAmount:
    amount: float
    unit: str
