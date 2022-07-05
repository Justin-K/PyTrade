class ValidationException(Exception):

    def __init__(self, msg: str):
        super().__init__(msg)


class AuthenticationException(Exception):

    def __init__(self, msg: str):
        super().__init__(msg)


class BalanceException(Exception):

    def __init__(self, msg: str):
        super().__init__(msg)
