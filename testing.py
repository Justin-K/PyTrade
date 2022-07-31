from datetime import datetime
from ccxt import kucoin
from random import choice, randrange, uniform, random
from trade import Trade
from base import OrderType

def tradeGenerator(num_trades: int):
    max_time = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())
    min_time = max_time - 86400000
    symbols = ["BTC/USDT", "PLAY/BTC", "PRE/BTC", "TOWER/BTC",
               "ABBC/BTC", "NMR/BTC", "CV/BTC", "TRB/BTC",
               "NWC/BTC", "PPT/BTC", "GOVI/BTC", "XHV/BTC"]
    client = kucoin()
    for _ in range(num_trades):
        symbol = choice(symbols)
        current_price = client.fetch_ticker(symbol)["last"]
        volume_quote = uniform(0.001, .5)
        trade = Trade(symbol, volume_quote)
        trade.initial_volume_base = current_price*volume_quote
        trade.time_bought_utc = randrange(min_time, max_time)
        trade.time_sold_utc = randrange(min_time, max_time)
        trade.buy_price_quote = current_price-(random()*randrange(1, 5)) if choice([True, False]) else current_price+(random()*randrange(1, 5))
        trade.sell_price_quote = current_price-(random()*randrange(1, 5)) if choice([True, False]) else current_price+(random()*randrange(1, 5))
        trade.buy_order_id = randrange(100000, 100000000)
        trade.sell_order_id = trade.buy_order_id + randrange(100000)
        trade.buy_order_type = choice([OrderType.LIMIT, OrderType.MARKET])
        trade.sell_order_type = choice([OrderType.LIMIT, OrderType.MARKET])
        # trade.final_volume_quote
        # trade.final_volume_base
        yield trade