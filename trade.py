from ccxt import Exchange
from enums import TradeType, OrderType
from errors import TradeError
from data_objects import Market, AssociatedAmount



class Trade:

    def __init__(self, market: Market, trade_type: str, quantity: AssociatedAmount, exchange_instance: Exchange):
        self.open_id: str = None
        self.close_id: str = None
        self.market: Market = market
        self.client = exchange_instance
        self.is_active: bool = False
        if trade_type == TradeType.LONG:
            self.trade_type: str = TradeType.LONG
        elif trade_type == TradeType.SHORT:
            self.trade_type: str = TradeType.SHORT
        else:
            raise TradeError("Unknown trade_type")
        if quantity.unit.upper() != market.quote_asset and quantity.unit.upper() != market.base_asset:
            raise TradeError(f"Unknown unit, \"{quantity.unit}\".")
        self.quantity: AssociatedAmount = quantity
        self.__base_quantity: AssociatedAmount = None

    # private
    def __convertQuantityBaseToQuote(self, original: AssociatedAmount, price: float) -> AssociatedAmount:
        return AssociatedAmount(price * original.amount, self.market.quote_asset)

    def __convertQuantityQuoteToBase(self, original: AssociatedAmount, price: float) -> AssociatedAmount:
        return AssociatedAmount(original.amount / price, self.market.base_asset)

    def __convertHelper(self, price: float = 0.0) -> float:
        if self.quantity.unit == self.market.quote_asset:
            if self.__base_quantity is None and price != 0.0:
                self.__base_quantity = self.__convertQuantityQuoteToBase(self.quantity, price)
            return self.__base_quantity.amount
        else:
            return self.quantity.amount

    ##########################################################################################################

    def openAtMarket(self):
        if self.is_active:
            raise TradeError("Trade has already been opened.")
        current = self.client.fetch_ticker(self.market.market_str)["last"]
        if self.trade_type == TradeType.LONG:
            self.open_id = self.client.create_market_buy_order(self.market.market_str, self.__convertHelper(current))["id"]
        else:  # we can use else instead of elif here because we would've raised an error already
            self.open_id = self.client.create_market_sell_order(self.market.market_str, self.__convertHelper(current))["id"]
        self.is_active = True

    def openAtPrice(self, price: AssociatedAmount):
        if price.unit != self.market.quote_asset:
            raise TradeError(f"Price must be in terms of \"{self.market.quote_asset}\".")
        if self.is_active:
            raise TradeError("Trade has already been opened.")
        current = self.client.fetch_ticker(self.market.market_str)["last"]
        if self.trade_type == TradeType.LONG:
            self.open_id = self.client.create_limit_buy_order(self.market.market_str, self.__convertHelper(current), price.amount)["id"]
        else:
            self.open_id = self.client.create_limit_sell_order(self.market.market_str, self.__convertHelper(current), price.amount)["id"]
        self.is_active = True

    def closeAtMarket(self):
        if not self.is_active:
            raise TradeError("Can't close a trade that hasn't been opened")
        if self.trade_type == TradeType.LONG:
            self.close_id = self.client.create_market_sell_order(self.market.market_str, self.__convertHelper())["id"]
        else:
            self.close_id = self.client.create_market_buy_order(self.market.market_str, self.__convertHelper())["id"]
        self.is_active = False

    def closeAtPrice(self, price: AssociatedAmount):
        if not self.is_active:
            raise TradeError("Can't close a trade that hasn't been opened")
        if price.unit != self.market.quote_asset:
            raise TradeError(f"Price must be in terms of \"{self.market.quote_asset}\".")
        open_price = self.client.fetch_order(self.open_id)["average"]
        if self.trade_type == TradeType.LONG:
            if price.amount < open_price:
                raise TradeError("Close price can't be less than open price for long trades.")
            self.close_id = self.client.create_limit_sell_order(self.market.market_str, self.__convertHelper(), price.amount)["id"]
        else:
            if price.amount > open_price:
                raise TradeError("Close price can't be greater than open price for short trades.")
            self.close_id = self.client.create_limit_buy_order(self.market.market_str, self.__convertHelper(), price.amount)["id"]
        # we don't set is_active = False here because the limit order placed may not fill immediately

    def cancelTrade(self):  # this method needs to be reworked, it errors out if either one of the orders is at market
        if self.is_active:
            if self.open_id is not None:
                order_type = self.client.fetch_order(self.open_id)["type"]  # Can't we deduce/get this offline somehow?
                if order_type == OrderType.LIMIT.value:
                    self.client.cancel_order(self.open_id)
            if self.close_id is not None:
                order_type = self.client.fetch_order(self.close_id)["type"]  # Can't we deduce/get this offline somehow?
                if order_type == OrderType.LIMIT.value:
                    self.client.cancel_order(self.close_id)
            self.is_active = False

    def profitLoss(self) -> AssociatedAmount:
        # Compute the P/L for the finished trade in terms of the quote unit
        # If the fee currency unit is not the quote unit, nothing happens (i.e. None is returned)
        # I think this should be fixed with some conversion magic, but I'm not worrying about it
        # at the moment
        if self.close_id is not None and self.open_id is not None:
            if self.quantity.unit == self.market.quote_asset:
                base_quantity = self.__base_quantity
            else:
                base_quantity = self.quantity
            open_order = self.client.fetch_order(self.open_id)
            close_order = self.client.fetch_order(self.close_id)
            if open_order["fee"]["currency"].upper() == self.market.quote_asset and close_order["fee"]["currency"].upper() == self.market.quote_asset:
                fee_open = AssociatedAmount(open_order["fee"]["cost"], self.market.quote_asset)
                fee_close = AssociatedAmount(close_order["fee"]["cost"], self.market.quote_asset)
                fees = fee_open.amount + fee_close.amount
                buy_price = open_order["average"] if self.trade_type == TradeType.LONG else close_order["average"]
                sell_price = close_order["average"] if self.trade_type == TradeType.LONG else open_order["average"]
                return AssociatedAmount(((sell_price - buy_price) * base_quantity.amount) - fees, self.market.quote_asset)

    def fetchCloseOrderStatus(self) -> str:
        if self.close_id and self.is_active:
            order = self.client.fetch_order(self.close_id)
            return order["status"]

    # def clear(self):
    #     self.__base_quantity = None
    #     self.open_id = None
    #     self.close_id = None
    #     self.is_active = False



if __name__ == "__main__":
    pass