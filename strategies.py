from base import BaseStrategy
from trade import Trade
from function_library import calculatePrice, average, s_to_ms


class SimpleSpotStrategy(BaseStrategy):

    def __init__(self, user_config, market, api):
        super().__init__(user_config, market, api)
        self.trade = Trade(self.market.symbol, self.config.quantity)

    def authenticate(self, is_sandbox=False):
        self.config.client = self.api_credentials.authenticateClient(sandbox_api=is_sandbox)
        self.config.client.check_required_credentials()
        self.authenticated = True

    def validate(self):
        super().validate()
        # verify that the user has enough available capital to run the strategy
        # ensure that the config is good (no empty values)

    def tick(self):
        price = self.config.client.fetchTicker(self.market.symbol)["last"]
        if self.trade.sell_order_id:
            pass
            # last_order = self.config.client.fetchOrder(self.trade.order_id)
            # if last_order["status"] == "closed":
            #     # we've filled a sell-order (aka completed a trade)
            #     now = self.config.client.milliseconds()
            #     utc_sold_time = now - s_to_ms(self.config.time_between_ticks)  # an approximation
            #     self.trade.time_sold_utc = utc_sold_time
            #     # determine and assign self.trade.sell_price here (i think??)
            #     self.trade.sell_price = self.config.client.fetchOrder(self.trade.order_id)["price"]
            #     self.onTradeCompletion(self.trade)
            #     # put thread to sleep here (self.config.time_between_ticks)
            # elif last_order["status"] in ["canceled", "expired", "rejected"]:
            #     raise Exception("The order has since been canceled, rejected, or it expired.")
        else:
            pass
            # if self.config.trade_min < price < self.config.trade_max:
            #     buy_order = self.config.client.createMarketBuyOrder(self.market.symbol, self.config.quantity)
            #     utc_buy_time = self.config.client.milliseconds()
            #     buy_price = buy_order["price"] if buy_order["price"] else buy_order["average"]
            #     # put thread to sleep here to allow the order to fill
            #     self.trade.time_bought_utc = average([utc_buy_time, buy_order["timestamp"]])
            #     self.trade.buy_price = buy_price
            #     self.trade.buy_order_id = buy_order["id"]
            #     # submit new limit-sell order here
            #     self.onTradeStart(self.trade)

    def onTradeStart(self, in_progress_trade: Trade):
        # register the new trade to be handled/monitored?
        pass

    def onTradeCompletion(self, finished_trade: Trade):
        self.trade = Trade(self.market.symbol, self.config.quantity)
        # log the finished trade in a db, pass off to a Reporter-type class, or both!

    def updateConfig(self, new_config, new_market=None, new_api=None):
        # give the user a way to change the config object (and the Market object as well) while the strategy is running
        pass


# implement a grid-like strategy (used to kill volatility)
class GridStrategy(BaseStrategy):
    pass


if __name__ == "__main__":
    pass
