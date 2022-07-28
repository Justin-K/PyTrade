class ValidationException(Exception):

    def __init__(self, msg: str):
        super().__init__(msg)


class AuthenticationException(Exception):

    def __init__(self, msg: str):
        super().__init__(msg)


class BalanceException(Exception):

    def __init__(self, msg: str):
        super().__init__(msg)


class CurrencyException(Exception):

    def __init__(self, msg: str):
        super().__init__(msg)


class MarketNotFoundError(Exception):

    def __init__(self, msg: str):
        super().__init__(msg)


class SettingsError(Exception):

    def __init__(self, msg: str):
        super().__init__(msg)


class OrderError(Exception):

    def __init__(self, msg: str):
        super().__init__(msg)

class ParameterError(Exception):

    def __init__(self, msg: str):
        super().__init__(msg)