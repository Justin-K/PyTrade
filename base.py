from ccxt import Exchange
from errors import ValidationException, AuthenticationException, MarketNotFoundError, SettingsError
from trade import Trade
from enum import Enum


class Market:

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.taker_fee = 0.002
        self.maker_fee = 0.0016
        self.base_asset = None
        self.quote_asset = None

    def setMarket(self, exchange: Exchange):
        exchange.load_markets()
        if self.symbol not in exchange.symbols:
            raise MarketNotFoundError(f"{self.symbol} market not found on exchange.")
        market = exchange.market(self.symbol)
        self.taker_fee = market["taker"] if market["taker"] != "" else self.taker_fee
        self.maker_fee = market["maker"] if market["maker"] != "" else self.maker_fee
        self.base_asset = market["base"]
        self.quote_asset = market["quote"]


class BaseAPI:

    def __init__(self):
        self.api_key = None
        self.api_secret = None

    def authenticateClient(self, sandbox_api=False):
        raise NotImplementedError("This method must be overridden in the derived class.")


class BaseUserConfig:

    def __init__(self):
        self.client = None
        self.take_profit = None
        self.quantity = None
        self.time_between_ticks = None


class BaseStrategy:

    def __init__(self, user_config, market, api):
        if not all([issubclass(type(user_config), BaseUserConfig),
                    issubclass(type(market), Market),
                    issubclass(type(api), BaseAPI)]):
            raise Exception("One or more parameter is not derived from the appropriate base class.")
        self.config = user_config
        self.market = market
        self.market.setMarket(self.config.client)
        self.api_credentials = api
        self.authenticated = False

    def authenticate(self):
        raise NotImplementedError("This method must be overridden in the derived class.")

    def validate(self):
        if not self.authenticated:
            raise ValidationException("A validation error has occurred.") \
                from AuthenticationException("Exchange instance is not authenticated (did you forget to call authenticate()?).")
        if None in self.config.__dict__.values() or \
                None in self.market.__dict__.values() or \
                None in self.api_credentials.__dict__.values():
            raise ValidationException("A validation error has occurred.") \
                from SettingsError("One or more setting is unset (aka the value for the setting is null).")

    def tick(self):
        raise NotImplementedError("This method must be overridden in the derived class.")

    def update(self, new_config, new_market=None, new_api=None):
        raise NotImplementedError("This method must be overridden in the derived class.")

    def onTradeComplete(self, finished_trade: Trade):
        raise NotImplementedError("This method must be overridden in the derived class.")

    def onTradeStart(self, in_progress_trade: Trade):
        raise NotImplementedError("This method must be overridden in the derived class.")

    def run(self):
        raise NotImplementedError("This method must be overridden in the derived class.")

    def stop(self):
        raise NotImplementedError("This method must be overridden in the derived class.")

    def restart(self):
        raise NotImplementedError("This method must be overridden in the derived class.")

class State(Enum):
    STOPPED = "The strategy is currently not running."
    RUNNING = "The strategy is currently running."
    ERROR = "The strategy encountered an error."
    WAITING = "The strategy is currently awaiting a start condition."


if __name__ == "__main__":
    pass
