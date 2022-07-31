from enum import Enum


class State(Enum):
    STOPPED: str = "The strategy is currently not running."
    RUNNING: str = "The strategy is currently running."
    ERROR: str = "The strategy encountered an error."
    WAITING: str = "The strategy is currently awaiting a condition."


class OrderType(Enum):
    MARKET: str = "market_order"
    LIMIT: str = "limit_order"


class OrderStatus(Enum):
    OPEN: str = "open"
    CLOSED: str = "closed"
    CANCELED: str = "canceled"
    EXPIRED: str = "expired"
    REJECTED: str = "rejected"


class TimeInForce(Enum):
    FOK: str = "fill_or_kill"
    IOC: str = "immediate_or_cancel"
    GTC: str = "good_till_canceled"
    PO: str = "post_only"


class Side(Enum):
    BUY: str = "buy"
    SELL: str = "sell"
