from ccxt import Exchange
from errors import ValidationException, AuthenticationException, MarketNotFoundError, SettingsError, ParameterError
from trade import Trade
from enum import Enum


class Market:

    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self.taker_fee: float = 0.002
        self.maker_fee: float = 0.0016
        self.base_asset = None
        self.quote_asset = None

    def setMarket(self, exchange: Exchange):
        exchange.load_markets()
        if self.symbol not in exchange.symbols:
            raise MarketNotFoundError(f"{self.symbol} market not found on exchange.")
        market = exchange.market(self.symbol)
        self.taker_fee: float = market["taker"] if market["taker"] != "" else self.taker_fee
        self.maker_fee: float = market["maker"] if market["maker"] != "" else self.maker_fee
        self.base_asset: str = market["base"]
        self.quote_asset: str = market["quote"]



class BaseAPI:

    def __init__(self):
        self.api_key = None
        self.api_secret = None
        self.is_sandbox_api = None

    def authenticateClient(self) -> Exchange:
        raise NotImplementedError("This method must be overridden in the derived class.")


class BaseUserConfig:

    def __init__(self):
        self.take_profit = None
        self.quantity = None
        self.time_between_ticks = None


class BaseStrategy:

    def __init__(self, user_config, market, api, name="New Strategy"):
        if not all([issubclass(type(user_config), BaseUserConfig),
                    issubclass(type(market), Market),
                    issubclass(type(api), BaseAPI)]):
            raise ParameterError("One or more parameter isn't a child of BaseAPI")
        self.authenticated = False
        self.config = user_config
        self.market = market
        self.api_credentials = api
        self.client = self.api_credentials.authenticateClient()
        self.client.check_required_credentials()
        self.authenticated = True
        self.market.setMarket(self.client)
        self.name = None

    # def authenticate(self):
    #     raise NotImplementedError("This method must be overridden in the derived class.")

    def validate(self):
        if not self.authenticated:
            raise ValidationException("A validation error has occurred.") \
                from AuthenticationException("Exchange instance is not authenticated.")
        if None in self.config.__dict__.values() or \
                None in self.market.__dict__.values() or \
                None in self.api_credentials.__dict__.values():
            raise ValidationException("A validation error has occurred.") \
                from SettingsError("One or more setting is unset (the value(s) for the setting(s) is null).")

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
    STOPPED: str = "The strategy is currently not running."
    RUNNING: str = "The strategy is currently running."
    ERROR: str = "The strategy encountered an error."
    WAITING: str = "The strategy is currently awaiting a condition."


class OrderType(Enum):
    MARKET: str = "market_order"
    LIMIT: str = "limit_order"


if __name__ == "__main__":
    pass
