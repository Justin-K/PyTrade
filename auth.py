from base import BaseAPI
from ccxt import kucoin


class KucoinAPI(BaseAPI):

    def __init__(self):
        super().__init__()
        self.password = None

    def authenticateClient(self, sandbox_api=False):
        if self.password is None or self.api_key is None or self.api_secret is None:
            raise Exception("One or more settings are unset.")
        else:
            client = kucoin({
                "apiKey": self.api_key,
                "secret": self.api_secret,
                "password": self.password
            })
            if sandbox_api:
                client.set_sandbox_mode(True)
                return client
            else:
                return client
