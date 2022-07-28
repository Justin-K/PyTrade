# This system is inspired by 3comma's smart trades
from base import Market, BaseAPI
from errors import ParameterError
from auth import KucoinAPI


class SmartTrade:

    def __init__(self, symbol: str, api_obj, is_sandbox=False):
        self.market = Market(symbol)
        if not issubclass(type(api_obj), BaseAPI):
            raise ParameterError("Parameter api_obj isn't a child of BaseAPI")
        self.api = api_obj
        self.client = self.api.authenticateClient(sandbox_api=is_sandbox)




if __name__ == "__main__":
    pass