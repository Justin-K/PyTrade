from generics import GenericStrategy
from errors import ValidationError
from trade import Trade
from enums import TradeType, OrderStatus
from function_library import calculatePrice, TimeframeToSeconds, percentage_to_decimal
from data_objects import AssociatedAmount
from threading import Event
from ccxt.base.errors import NetworkError
from debug_logging import DebugLogger
from traceback import print_exc


class SimpleStrategy(GenericStrategy):

    def __init__(self, user_config, api_object, market, name="SimpleStrategy"):
        super().__init__(user_config, api_object, market, name=name)
        self.trade: Trade = Trade(self.market, TradeType.LONG, self.config.quantity, self.client)
        self.event = Event()
        # Debug
        self.logger = DebugLogger(f"{self.name}.txt")
        self.can_update = True
        self.total_pnl = AssociatedAmount(0.0, self.market.quote_asset)
        self.num_closed_trades: int = 0

    def validate(self):
        super().validate()
        if self.config.min_allowed_price.unit != self.market.quote_asset or \
                self.config.max_allowed_price.unit != self.market.quote_asset:
            raise ValidationError("Trading bounds not in terms of quote unit.")
        if not (self.config.min_allowed_price.amount < self.config.max_allowed_price.amount):
            raise ValidationError("Improper trading bounds.")
        if self.config.cooldown_period.amount <= 0.0:
            raise ValidationError("Improper cool down period.")
        TimeframeToSeconds(self.config.cooldown_period.unit)

    def tick(self):
        if not self.trade.is_active:
            current = self.client.fetchTicker(self.market.market_str)
            if self.config.min_allowed_price.amount <= current["last"] <= self.config.max_allowed_price.amount:
                self.can_update = False
                self.trade.openAtMarket()
                buy_price = self.client.fetchOrder(self.trade.open_id)["average"]
                debug_qty = self.trade.quantity if self.trade.quantity.unit == self.market.base_asset else self.trade.quantity.amount/buy_price
                self.logger.log(f"Opened {self.trade.trade_type} trade at {buy_price} {self.market.quote_asset} for {debug_qty} {self.market.base_asset}. Order ID: {self.trade.open_id}")
                self.client.sleep(250)
                sell_price = calculatePrice(buy_price, percentage_to_decimal(self.config.take_profit), [0.002, 0.0016])
                self.trade.closeAtPrice(AssociatedAmount(sell_price, self.market.quote_asset))
                self.logger.log(f"Posted limit-sell order for {debug_qty} {self.market.base_asset} at {sell_price} {self.market.quote_asset}. Order ID: {self.trade.close_id}")
                self.can_update = True
        else:
            if self.trade.fetchCloseOrderStatus() == OrderStatus.CLOSED.value:
                self.total_pnl.amount += self.trade.profitLoss().amount
                self.num_closed_trades += 1
                self.trade.is_active = False
                self.logger.log(f"Trade closed. Open ID: {self.trade.open_id} | Close ID: {self.trade.close_id} | P/L: {self.trade.profitLoss()}")
                self.logger.log(f"Entering wait period of {TimeframeToSeconds(self.config.cooldown_period.unit, multiplier=self.config.cooldown_period.amount)} seconds.")
                self.trade = None
                self.trade = Trade(self.market, TradeType.LONG, self.config.quantity, self.client)
                self.event.wait(TimeframeToSeconds(self.config.cooldown_period.unit, multiplier=self.config.cooldown_period.amount))

    def run(self):
        self.validate()
        self.logger.log("Settings validation successful. Starting...")
        while not self.event.is_set():
            try:
                self.tick()
                self.event.wait(TimeframeToSeconds(self.config.time_between_ticks.unit, multiplier=self.config.time_between_ticks.amount))
            except NetworkError:
                self.logger.log("Network error. Ignoring...")
            except Exception as e:
                self.logger.log(f"Fatal error occurred. {print_exc()}")
                raise e
        self.logger.log("Stopped.")

    def stop(self):
        if self.trade.is_active:
            self.logger.log("Stop function called. Canceling all outstanding orders and halting...")
            self.trade.cancelTrade()
            self.event.set()

    def update(self, new_config):
        if self.can_update:
            self.config = new_config
            self.trade.quantity = self.config.quantity
            self.logger.log("Config updated.")
