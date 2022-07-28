from function_library import profitLoss, ms_to_s, from_utc_timestamp_to_local_datetime


class Trade:

    # a trade (hypothetically at least) is defined by 2 orders: a buy order and a sell order
    def __init__(self, symbol: str, volume):
        self.symbol = symbol.upper()
        self.volume_quote = volume
        self.volume_base = None
        self.time_bought_utc = None
        self.time_sold_utc = None
        self.buy_price = None
        self.sell_price = None
        self.buy_order_id = None
        self.sell_order_id = None

    @property
    def profit(self):
        return profitLoss(self.buy_price, self.sell_price, self.volume_quote)

    @property
    def execution_time(self):
        if self.time_sold_utc > self.time_bought_utc:
            ms_time = self.time_sold_utc - self.time_bought_utc
        else:
            ms_time = self.time_bought_utc - self.time_sold_utc
        assert ms_time > 0
        return ms_to_s(ms_time)

    @property
    def time_bought_local_datetime(self):
        return from_utc_timestamp_to_local_datetime(self.time_bought_utc)

    @property
    def time_sold_local_datetime(self):
        return from_utc_timestamp_to_local_datetime(self.time_sold_utc)

    @property
    def gain(self):
        return (self.profit / (self.buy_price * self.volume_quote)) * 100

    def __repr__(self):
        sign = "+" if self.profit > 0 else ""
        return f"Symbol: {self.symbol} | Net: {sign+str(round(self.gain, 2))+'%'}"


if __name__ == "__main__":
    pass