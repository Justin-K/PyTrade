from base import BaseUserConfig


class SimpleSpotStrategyConfig(BaseUserConfig):

    def __init__(self):
        super().__init__()
        self.trade_min = None
        self.trade_max = None
        self.cooldown_period = None


class SmartTradeConfig(BaseUserConfig):

    def __init__(self):
        super().__init__()
        self.stop_loss = {
            "stop_loss_enabled": None,
            "stop_loss_percent": None,
            "stop_loss_price": None,
            "stop_loss_order_type": None,
        }
        self.take_profit = {
            "take_profit_percent": None,
            "take_profit_price": None,
            "take_profit_order_type": None,
        }