class Error(Exception):
    def __init__(self, message: str = "", type: str = None):
        self.message = message
        self.type = type
        super().__init__(message)


class NotOk(Error):
    def __init__(self, message: str = ""):
        super().__init__(message, type="NotOk")


class Unauthorized(Error):
    def __init__(self, message: str = ""):
        super().__init__(message, type="Unauthorized")
