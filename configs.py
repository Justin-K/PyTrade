from generics import GenericUserConfig, GenericStrategy
from data_objects import AssociatedAmount, Market


class SimpleStrategyConfig(GenericUserConfig):

    def __init__(self):
        super().__init__()
        self.min_allowed_price: AssociatedAmount = None
        self.max_allowed_price: AssociatedAmount = None
        self.cooldown_period: AssociatedAmount = None
