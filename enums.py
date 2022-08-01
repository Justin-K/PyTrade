from enum import Enum


class State(Enum):
    STOPPED: str = "The strategy is currently not running."
    RUNNING: str = "The strategy is currently running."
    ERROR: str = "The strategy encountered an error."
    WAITING: str = "The strategy is currently awaiting a condition."


class OrderType(Enum):
    MARKET: str = "market"
    LIMIT: str = "limit"


class OrderStatus(Enum):
    OPEN: str = "open"
    CLOSED: str = "closed"
    CANCELED: str = "canceled"
    EXPIRED: str = "expired"
    REJECTED: str = "rejected"


class TimeInForce(Enum):
    FOK: str = "FOK"  # fill or kill
    IOC: str = "IOC"  # immediate or canceled
    GTC: str = "GTC"  # good 'till canceled
    PO: str = "PO"  # post only


class Side(Enum):
    BUY: str = "buy"
    SELL: str = "sell"
