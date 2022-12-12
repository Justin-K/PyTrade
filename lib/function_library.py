from datetime import datetime, timezone
from dateutil import tz
from typing import Tuple

from lib.errors import SeperatorError


def decimal_to_percentage(x):
    return x * 100


def percentage_to_decimal(x):
    return x / 100


def ms_to_s(ms: int):
    return 0.001*ms


def s_to_ms(s):
    return s/0.001


def profitLoss(buy_price, sell_price, qty):  # (sell_price_quote - buy_price) * qty
    return (sell_price - buy_price) * qty


def calculatePrice(initial_price, desired_profit, offsets: list):
    # each member of "offsets" MUST be in decimal form, i.e. pass .7, and it'll be interpreted as 70%
    # desired_profit must also be in decimal form, i.e. pass .05, and it'll be interpreted as 5%
    offset_sum = sum([i for i in offsets]) if offsets else 0
    return (initial_price * (desired_profit + offset_sum)) + initial_price


def inRange(num, percent, value):  # is num within percent% of value?
    upper = value+(value*percent)
    lower = value-(value*percent)
    if lower <= num <= upper:
        return True
    else:
        return False


def from_utc_timestamp_to_local_datetime(utc_timestamp: int) -> datetime:  # credit to MrFuppes on StackOverflow
    local_tz = datetime.now(timezone.utc).astimezone().tzinfo
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz(local_tz.__str__())
    utc = datetime.utcfromtimestamp(utc_timestamp/1000)
    utc = utc.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone)


def average(data: list):
    return sum(data)/len(data)


def seperatePair(symbol: str) -> Tuple[str, str]:
    separators = ["/", "-", "_"]
    separator = None
    sbml = symbol.upper()
    for char in sbml:
        if char in separators:
            separator = char
            break
    if separator is None:
        raise SeperatorError(f"A valid separator was not found. Base and quote asset deduction failed. ({symbol})")
    else:
        splt = sbml.split(separator)
        return splt[0], splt[1]


if __name__ == "__main__":
    pass