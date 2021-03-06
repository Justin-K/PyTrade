from strategies import SimpleSpotStrategy
from base import Market
from config import SimpleSpotStrategyConfig
from auth import KucoinAPI
from ccxt import kucoin

config = SimpleSpotStrategyConfig()
config.quantity = 2500
config.client = kucoin()
config.time_between_ticks = 30
config.take_profit = 0.5
config.trade_min = 15000
config.trade_max = 25000
config.cooldown_period = 30

market = Market("BTC/USDT")
market.setMarket(config.client)

api_real = KucoinAPI()
api_real.api_key = ""
api_real.api_secret = ""
api_real.password = ''

sandbox_api = KucoinAPI()
sandbox_api.api_key = ""
sandbox_api.api_secret = ""
sandbox_api.password = ''


# strategy = SimpleSpotStrategy(config, market, sandbox_api)
# strategy.authenticate(True)
# strategy.validate()



# buy give quote currency and receive base currency; for example, buying BTC/USD means that you will receive bitcoins for your dollars.
# sell give base currency and receive quote currency; for example, buying BTC/USD means that you will receive dollars for your bitcoins.