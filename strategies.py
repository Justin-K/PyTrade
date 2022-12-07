from lib.base import BaseStrategy
from lib.enums import State, OrderStatus
from lib.trade import Trade
from ccxt.base.errors import NetworkError
from lib.function_library import calculatePrice, percentage_to_decimal
from lib.errors import ValidationException, CurrencyException, BalanceException, OrderError
from threading import Event


class SimpleSpotStrategy(BaseStrategy):

    def __init__(self, user_config, market, api):
        super().__init__(user_config, market, api)
        self.trade = Trade(self.market.symbol, self.config.quantity)
        self.event = Event()
        self.state = State.STOPPED

    def validate(self):
        super().validate()
        # provide a method to validate that the strategy can run (i.e. check settings validity, account balances, etc.)
        # this method will run once
        balance_struct = self.client.fetchBalance()
        if self.market.quote_asset not in balance_struct["free"].keys() or balance_struct["free"][
            self.market.quote_asset] == 0:
            raise ValidationException("A validation error has occurred.") \
                from CurrencyException(f"No {self.market.quote_asset} available to trade.")
        if self.config.quantity > balance_struct["free"][self.market.quote_asset]:
            raise ValidationException("A validation error has occurred.") \
                from BalanceException(
                f"Designated quantity is larger than the available quantity of {self.market.quote_asset} to trade.")

    def tick(self):
        # for this strategy we want to place a buy order, calculate a sell price based on provided params,
        # then place a limit-sell order for the bought volume_quote at that price. We wait for the sell order to fill,
        # then sleep for SimpleSpotStrategyConfig.cooldown_period seconds. rinse and repeat.
        # also, we can't poll the exchange "instantly" (this will exceed the rate limit of basically any exchange).
        # To overcome this, we will sleep for BaseConfig.time_between_ticks seconds between calling the tick() method.
        # Also, set all the fields in self.trade:
        pass

    def onTradeStart(self, in_progress_trade: Trade):
        # register the new trade to be handled/monitored?
        pass

    def onTradeComplete(self, finished_trade: Trade):
        # log the finished trade in a db, pass off to a Reporter-type class, or both!
        pass

    def update(self, new_config, new_market=None, new_api=None):
        # give the user a way to change the config object (and the Market object as well) while the strategy is running
        pass

    def run(self):
        # begin execution of the strategy, this method functions as the class's "main loop"
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
