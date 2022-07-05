from base import BaseUserConfig


class SimpleSpotStrategyConfig(BaseUserConfig):

    def __init__(self):
        super().__init__()
        self.trade_min = None
        self.trade_max = None
