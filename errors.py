class RuntimeException(RuntimeError):
    def __init__(self, token, message):
        self.token = token
        self.message = message
