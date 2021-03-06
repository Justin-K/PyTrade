from base import BaseStrategy, State
from trade import Trade
from ccxt.base.errors import NetworkError
from function_library import calculatePrice, average, s_to_ms, percentage_to_decimal
from time import sleep
from errors import ValidationException, CurrencyException, BalanceException, OrderError
from threading import Event


class SimpleSpotStrategy(BaseStrategy):

    def __init__(self, user_config, market, api):
        super().__init__(user_config, market, api)
        self.trade = Trade(self.market.symbol, self.config.quantity)
        self.event = Event()
        self.state = State.STOPPED

    def authenticate(self, is_sandbox=False):
        self.config.client = self.api_credentials.authenticateClient(sandbox_api=is_sandbox)
        self.config.client.check_required_credentials()
        self.authenticated = True

    def validate(self):
        super().validate()
        balance_struct = self.config.client.fetchBalance()
        if self.market.quote_asset not in balance_struct["free"].keys() or balance_struct["free"][self.market.quote_asset] == 0:
            raise ValidationException("A validation error has occurred.") \
                from CurrencyException(f"No {self.market.quote_asset} available to trade.")
        if self.config.quantity > balance_struct["free"][self.market.quote_asset]:
            raise ValidationException("A validation error has occurred.") \
                from BalanceException(f"Designated quantity is larger than the available quantity of {self.market.quote_asset} to trade.")

    def tick(self):
        # for this strategy we want to place a buy order, calculate a sell price based on provided params,
        # then place a limit-sell order for the bought volume_quote at that price. We wait for the sell order to fill,
        # then sleep for SimpleSpotStrategyConfig.cooldown_period seconds. rinse and repeat.
        # also, we can't poll the exchange "instantly" (this will exceed the rate limit of basically any exchange).
        # To overcome this, we will sleep for BaseConfig.time_between_ticks seconds between calling the tick() method.
        # Also, set all the fields in self.trade:
        # Trade.time_bought_utc x
        # Trade.time_sold_utc x
        # Trade.buy_price x
        # Trade.sell_price x
        # Trade.buy_order_id x
        # Trade.sell_order_id x
        # Trade.volume_base x
        if self.trade.sell_order_id and self.trade.buy_order_id:  # an initial (market) buy order has been filled and a sell order has been placed
            sell_order = self.config.client.fetchOrder(self.trade.sell_order_id)
            if sell_order["status"] == "closed":  # the sell order has filled, successfully completing a trade
                self.trade.sell_price = sell_order["price"]
                ms_now = self.config.client.milliseconds()
                tbt = self.config.time_between_ticks
                self.trade.time_sold_utc = sell_order["lastTradeTimestamp"] if sell_order["lastTradeTimestamp"] else (ms_now - s_to_ms(tbt))
                self.onTradeComplete(self.trade)
            elif sell_order["status"] in ["expired", "rejected", "canceled"]:  # the sell order has expired, been rejected or canceled
                raise OrderError(f"The sell order (id: {self.trade.sell_order_id}) has since been rejected, canceled, or it expired")
        if not self.trade.buy_order_id:  # a buy order has yet to be placed
            assert not self.trade.sell_order_id
            price = self.config.client.fetchTicker(self.market.symbol)["last"]
            if self.config.trade_min < price < self.config.trade_max:  # check if the price of the commodity is in the range provided
                self.state = State.RUNNING if self.state == State.WAITING else self.state  # make sure this line won't be a trouble-maker :)
                buy_order = self.config.client.createMarketBuyOrder(self.market.symbol, self.config.quantity)
                self.event.wait(.5)
                self.trade.time_bought_utc = average([buy_order["timestamp"], self.config.client.milliseconds()])
                self.trade.buy_order_id = buy_order["id"]
                self.trade.volume_base = buy_order["cost"]  # ?????? works??
                self.trade.buy_price = buy_order["price"] if buy_order["price"] else price
                sell_price = calculatePrice(self.trade.buy_price,
                                            percentage_to_decimal(self.config.take_profit),
                                            [self.market.maker_fee, self.market.taker_fee])
                sell_order = self.config.client.createLimitSellOrder(self.market.symbol, self.config.quantity, sell_price)
                self.trade.sell_order_id = sell_order["id"]
                self.onTradeStart(self.trade)

            else:
                self.state = State.WAITING

    def onTradeStart(self, in_progress_trade: Trade):
        # register the new trade to be handled/monitored?
        with open("debug.txt", "a") as f:
            f.write(str(self.trade.symbol) + "\n")
            f.write(str(self.trade.volume_quote) + "\n")
            f.write(str(self.trade.volume_base) + "\n")
            f.write(str(self.trade.time_bought_utc) + "\n")
            f.write(str(self.trade.time_sold_utc) + "\n")
            f.write(str(self.trade.buy_price) + "\n")
            f.write(str(self.trade.sell_price) + "\n")
            f.write(str(self.trade.buy_order_id) + "\n")
            f.write(str(self.trade.sell_order_id) + "\n")

    def onTradeComplete(self, finished_trade: Trade):
        self.trade = Trade(self.market.symbol, self.config.volume_quote)
        # log the finished trade in a db, pass off to a Reporter-type class, or both!
        self.event.wait(self.config.cooldown_period)

    def update(self, new_config, new_market=None, new_api=None):
        # give the user a way to change the config object (and the Market object as well) while the strategy is running
        self.config = new_config
        if new_market:
            self.market = new_market
        if new_api:
            self.api_credentials = new_api

    def run(self):
        self.validate()
        self.state = State.RUNNING
        while not self.event.is_set():
            try:
                self.tick()
                self.event.wait(self.config.time_between_ticks)
            except NetworkError:
                pass
            except Exception as e:
                self.state = State.ERROR
                # handle error here
                raise e
        self.state = State.STOPPED

    def stop(self):
        self.event.set()

    def restart(self):
        self.event.clear()
        self.run()

# implement a grid-like strategy (used to kill volatility)
class GridStrategy(BaseStrategy):
    pass


if __name__ == "__main__":
    pass
