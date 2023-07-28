from typing import Tuple
from errors import SeperatorError, UnsupportedTimeframeError
from enums import Timeframe


def decimal_to_percentage(x):
    return x * 100


def percentage_to_decimal(x):
    return x / 100


def seperatePair(symbol: str) -> Tuple[str, str]:
    separators = ["/", "-", "_"]
    for char in separators:
        if symbol.count(char) > 1:
            raise SeperatorError("Malformed symbol, symbol can't have multiple separators.")
    separator = None
    sbml = symbol.upper()
    for char in sbml:
        if char in separators:
            separator = char
            break
    if separator is None:
        raise SeperatorError(f"A valid separator was not found. Base and quote asset deduction failed. ({symbol})")
    splt = sbml.split(separator)
    return splt[0], splt[1]


def TimeframeToSeconds(tf: str, multiplier: float = 1.0) -> float:
    mapper = {
        Timeframe.ONE_MINUTE: 60,
        Timeframe.ONE_HOUR: 3600,
        Timeframe.ONE_DAY: 86400,
    }
    if tf not in mapper.keys():
        raise UnsupportedTimeframeError("Passed Timeframe is either not a Timeframe or is too long.")
    return mapper[tf] * multiplier


def calculatePrice(initial_price, desired_profit, offsets: list):
    # each member of "offsets" MUST be in decimal form, i.e. pass .7, and it'll be interpreted as 70%
    # desired_profit must also be in decimal form, i.e. pass .05, and it'll be interpreted as 5%
    offset_sum = sum([i for i in offsets]) if offsets else 0
    return (initial_price * (desired_profit + offset_sum)) + initial_price