from base import BaseStrategy, State
from trade import Trade
from ccxt.base.errors import NetworkError
from function_library import calculatePrice, average, s_to_ms
from time import sleep
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
        # verify that the user has enough available capital to run the strategy
        # ensure that the config is good (no empty values)

    def tick(self):
        pass

    def onTradeStart(self, in_progress_trade: Trade):
        # register the new trade to be handled/monitored?
        pass

    def onTradeCompletion(self, finished_trade: Trade):
        self.trade = Trade(self.market.symbol, self.config.quantity)
        # log the finished trade in a db, pass off to a Reporter-type class, or both!

    def updateConfig(self, new_config, new_market=None, new_api=None):
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

    # def reset(self):
    #     self.event.clear()




# implement a grid-like strategy (used to kill volatility)
class GridStrategy(BaseStrategy):
    pass


if __name__ == "__main__":
    pass
