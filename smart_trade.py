# This system is inspired by 3comma's smart trades
from base import Market, BaseAPI, BaseStrategy
from errors import ParameterError
from auth import KucoinAPI
from trade import Trade


class SmartTrade(BaseStrategy):

    def __init__(self, user_config, market, api):
        super().__init__(user_config, market, api)

    def tick(self):
        # check status of order(s) and react accordingly
        pass

    def run(self):
        # perform computations and decisions on the provided settings here
        # then place the appropriate type of order
        pass

    def update(self, new_config, new_market=None, new_api=None):
        # provide a way to update the SmartTrade
        pass

    def stop(self):
        # cancel all outstanding orders and perform other duties
        pass

    def onTradeStart(self, in_progress_trade: Trade):
        # perform trading logic before initial order is placed here
        pass

    def onTradeComplete(self, finished_trade: Trade):
        # perform "wrap-up" duties here
        pass

    def validate(self):
        # insure the SmartTrade can execute without issue as much as possible
        pass

    def restart(self):
        # I'm not sure that this method applies...
        pass







if __name__ == "__main__":
    pass
