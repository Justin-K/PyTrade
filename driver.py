from apis import KucoinAPI
from strategies import SimpleStrategy
from configs import SimpleStrategyConfig
from data_objects import AssociatedAmount, Market
from enums import Timeframe, OrderStatus
from threading import Thread

kucoin_api = KucoinAPI()
kucoin_api.settings["api_key"] = ""
kucoin_api.settings["api_secret"] = ""
kucoin_api.settings["password"] = ""
kucoin_api.settings["is_sandbox_api"] = False

config = SimpleStrategyConfig()
config.quantity = AssociatedAmount(0.038, "BTC")
config.cooldown_period = AssociatedAmount(30, Timeframe.ONE_MINUTE)
config.max_allowed_price = AssociatedAmount(0.0012372, "BTC")
config.min_allowed_price = AssociatedAmount(0.0012073, "BTC")
config.take_profit = 0.1
config.time_between_ticks = AssociatedAmount(5, Timeframe.ONE_MINUTE)

strat = SimpleStrategy(config, kucoin_api, Market("ZEC/BTC"), "ZcashBot")

def generateNewConfig() -> SimpleStrategyConfig:
    tmp_timeframe = {
        Timeframe.ONE_MINUTE: "minutes",
        Timeframe.ONE_HOUR: "hours",
        Timeframe.ONE_DAY: "days"
    }
    new_c = strat.config
    print("For any prompt, enter \"old\" to maintain setting's original value.")
    qty_prompt = input(f"New quantity (current = {new_c.quantity.amount} {new_c.quantity.unit}): ")
    new_cooldown_prompt = input(f"New cooldown period (current = {new_c.cooldown_period.amount} {tmp_timeframe[new_c.cooldown_period.unit]}): ")
    max_price_prompt = input(f"New max price (current = {new_c.max_allowed_price.amount} {new_c.max_allowed_price.unit}): ")
    min_price_prompt = input(f"New min price (current = {new_c.min_allowed_price.amount} {new_c.min_allowed_price.unit}): ")
    tp_prompt = input(f"New take profit (current = {new_c.take_profit}%): ")
    tbt_prompt = input(f"New time between ticks (current = {new_c.time_between_ticks.amount} {tmp_timeframe[new_c.time_between_ticks.unit]}): ")
    new_qty = new_c.quantity if qty_prompt == "old" else AssociatedAmount(float(qty_prompt.split(" ")[0]), qty_prompt.split(" ")[1])
    new_cool_p = new_c.cooldown_period if new_cooldown_prompt == "old" else AssociatedAmount(float(new_cooldown_prompt), new_c.cooldown_period.unit)
    new_max_price = new_c.max_allowed_price if max_price_prompt == "old" else AssociatedAmount(float(max_price_prompt), new_c.max_allowed_price.unit)
    new_min_price = new_c.min_allowed_price if min_price_prompt == "old" else AssociatedAmount(float(min_price_prompt), new_c.min_allowed_price.unit)
    new_tp = new_c.take_profit if tp_prompt == "old" else float(tp_prompt)
    new_tbt = new_c.time_between_ticks if tbt_prompt == "old" else AssociatedAmount(float(tbt_prompt), new_c.time_between_ticks.unit)

    new_c.quantity = new_qty
    new_c.cooldown_period = new_cool_p
    new_c.max_allowed_price = new_max_price
    new_c.min_allowed_price = new_min_price
    new_c.take_profit = new_tp
    new_c.time_between_ticks = new_tbt
    return new_c



# quick n' dirty menu-style interface

def menu(selection: str):
    if selection == "report":
        print(f"Total profit: {round(strat.total_pnl.amount,6)} {strat.total_pnl.unit}")
        # if strat.trade.open_id and strat.trade.close_id:
        #     print(f"Active trade P/L: {round(strat.trade.profitLoss().amount,6)} {strat.trade.profitLoss().unit}")
        print(f"Number of closed trades: {strat.num_closed_trades}")
        menu(input("--> "))
    elif selection == "update":
        if strat.can_update:
            strat.update(generateNewConfig())
            menu(input("--> "))
        else:
            print("In the middle of placing an order, try again momentarily.")
            menu(input("--> "))
    elif selection == "stop":
        strat.stop()
        exit(0)
    elif selection == "run":
        if strat.trade.is_active:
            print("Already running.")
        else:
            t = Thread(target=strat.run).start()
        menu(input("--> "))
    elif selection == "help":
        print("Valid Selections:")
        print("report")
        print("update")
        print("stop")
        print("run")
        print("help")
        menu(input("--> "))
    else:
        print("Unrecognized selection.")
        menu(input("--> "))
menu(input("--> "))
