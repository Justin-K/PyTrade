from ccxt import Exchange
from abc import ABCMeta, abstractmethod
from data_objects import AssociatedAmount, Market
from errors import SettingsError, ValidationError, AuthenticationError
from enums import Timeframe

class GenericAPI(metaclass=ABCMeta):

    def __init__(self):
        self.settings = {
            "api_key": None,
            "api_secret": None,
            "is_sandbox_api": None
        }

    @abstractmethod
    def authenticateClient(self) -> Exchange:
        pass


class GenericUserConfig(metaclass=ABCMeta):

    def __init__(self):
        self.take_profit: float = None
        self.quantity: AssociatedAmount = None
        self.time_between_ticks: AssociatedAmount = None


class GenericStrategy(metaclass=ABCMeta):

    def __init__(self, user_config, api_object, market, name="New Strategy"):
        if not all([issubclass(type(user_config), GenericUserConfig),
                    issubclass(type(market), Market),
                    issubclass(type(api_object), GenericAPI)]):
            raise SettingsError("One or more parameters are not a subclass of the appropriate type.")
        self.config = user_config
        self.api = api_object
        self.market = market
        self.name = name
        self.client = self.api.authenticateClient()
        self.authenticated = True

    @abstractmethod
    def validate(self):
        if self.config.quantity.unit != self.market.quote_asset and self.config.quantity.unit != self.market.base_asset:
            raise ValidationError(f"Unknown unit, \"{self.config.quantity.unit}\"")
        if not self.authenticated:
            raise ValidationError("A validation error has occurred.") from AuthenticationError("Improper credentials.")
        if None in self.config.__dict__.values() or \
                None in self.market.__dict__.values():
            raise ValidationError("A validation error has occurred.") from SettingsError("Improper value for one or more settings, None.")

    @abstractmethod
    def tick(self):
        pass

    @abstractmethod
    def update(self, new_config):
        pass

    # @abstractmethod
    # def onTradeComplete(self):
    #     pass
    #
    # @abstractmethod
    # def onTradeStart(self):
    #     pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    # @abstractmethod
    # def restart(self):
    #     pass
