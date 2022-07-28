# This system is inspired by 3comma's smart trades

from base import Market, BaseAPI, BaseStrategy
from errors import ParameterError
from auth import KucoinAPI


class SmartTrade(BaseStrategy):

    def __init__(self, user_config, market, api):
        super().__init__(user_config, market, api)








if __name__ == "__main__":
    pass