class RuntimeException(RuntimeError):
    def __init__(self, token, message):
        self.token = token
        self.message = message


class Return(RuntimeException):
    """return statements use exceptional control flow to return a value"""
    def __init__(self, value):
        self.value = value
