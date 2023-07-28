from datetime import datetime


class DebugLogger:

    def __init__(self, fname: str):
        self.fn = fname

    def log(self, msg: str):
        with open(self.fn, "a") as f:
            f.write(datetime.now().strftime(f"%m-%d-%Y %H:%M:%S | {msg}\n"))
