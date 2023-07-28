from generics import GenericAPI
from ccxt import kucoin


class KucoinAPI(GenericAPI):

    def __init__(self):
        super().__init__()
        self.settings["password"] = None

    def authenticateClient(self) -> kucoin:
        if None in self.settings.values():
            raise Exception("One or more settings are unset.")
        client = kucoin({
            "apiKey": self.settings["api_key"],
            "secret": self.settings["api_secret"],
            "password": self.settings["password"]
        })
        client.check_required_credentials()  # may not be needed
        if self.settings["is_sandbox_api"]:
            client.set_sandbox_mode(True)
            return client
        else:
            return client
