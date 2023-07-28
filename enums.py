from enum import Enum


class Side(Enum):
    BUY: str = "buy"
    SELL: str = "sell"


class TradeType(Enum):
    LONG: str = "long"
    SHORT: str = "short"


class Timeframe(Enum):
    ONE_MINUTE: str = "1m"
    ONE_HOUR: str = "1h"
    ONE_DAY: str = "1d"
    ONE_MONTH: str = "1M"
    ONE_YEAR: str = "1y"


class TimeInForce(Enum):
    FOK: str = "FOK"  # fill or kill
    IOC: str = "IOC"  # immediate or canceled
    GTC: str = "GTC"  # good 'till canceled
    PO: str = "PO"  # post only


class OrderStatus(Enum):
    OPEN: str = "open"
    CLOSED: str = "closed"
    CANCELED: str = "canceled"
    EXPIRED: str = "expired"
    REJECTED: str = "rejected"


class OrderType(Enum):
    MARKET: str = "market"
    LIMIT: str = "limit"
