from ccxt import Exchange
from typing import List
from errors import ValidationException, AuthenticationException, SettingsError, ParameterError
from trade import Trade
from enums import Timeframe
from function_library import seperatePair


# dataclass doesn't work here because symbol must be defined
class Market:

    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self.taker_fee: float = 0.002
        self.maker_fee: float = 0.0016
        # instead of getting base and quote from an authenticated Exchange object, we deduce it from the symbol itself
        seperated = seperatePair(self.symbol)
        self.base_asset = seperated[0]
        self.quote_asset = seperated[1]


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
        self.name = name

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


class Candle:

    def __init__(self):
        self.utc_timestamp = None
        self.open_price = None
        self.highest_price = None
        self.lowest_price = None
        self.closing_price = None
        self.volume_base = None  # *usually* in terms of the base currency


class Chart:

    def __init__(self, symbol: str, time_frame: Timeframe, client: Exchange, since=None):
        self.symbol = symbol.upper()
        self.time_frame = time_frame
        self.client = client
        self.start_time = since  # "...is an integer UTC timestamp in milliseconds"

    @property
    def candles(self):
        candles: List[Candle] = []
        data = self.client.fetch_ohlcv(self.symbol, self.time_frame.value, since=self.start_time)
        for ohlcv in data:
            candle = Candle()
            candle.utc_timestamp = ohlcv[0]
            candle.open_price = ohlcv[1]
            candle.highest_price = ohlcv[2]
            candle.lowest_price = ohlcv[3]
            candle.closing_price = ohlcv[4]
            candle.volume_base = ohlcv[5]
            candles.append(candle)
        return candles


if __name__ == "__main__":
    x = Market("BTC/USDT")
    print(x.quote_asset)
