from errors import RuntimeException


class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def get(self, name):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeException(
            token=name,
            message=f"Undefined variable '{name.lexeme}'.",
        )

    def assign(self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name=name, value=value)
            return

        raise RuntimeException(
            token=name,
            message=f"Cannot assign: undefined variable '{name.lexeme}'.",
        )

    def define(self, name, value):
        self.values[name] = value
