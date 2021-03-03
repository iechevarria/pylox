from .exceptions import RuntimeException


class Environment:
    def __init__(self, enclosing=None):
        """Stores variables and the environment's enclosing environment

        The enclosing environment is used for traversing up scopes to find if a
        variable is defined, or for traversing up a pre-determined number of
        scopes (ultimately provided by Resolver class)
        """
        self.values = {}
        self.enclosing = enclosing

    def get(self, name):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        # traverse up environments to find if variable is defined
        if self.enclosing is not None:
            return self.enclosing.get(name=name)

        raise RuntimeException(
            token=name,
            message=f"Undefined variable '{name.lexeme}'.",
        )

    def assign(self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        # traverse up environments to find variable
        if self.enclosing is not None:
            self.enclosing.assign(name=name, value=value)
            return

        raise RuntimeException(
            token=name,
            message=f"Undefined variable '{name.lexeme}'.",
        )

    def define(self, name, value):
        self.values[name] = value

    def get_at(self, distance, name):
        return self.ancestor(distance).values[name]

    def assign_at(self, distance, name, value):
        self.ancestor(distance).values[name.lexeme] = value

    def ancestor(self, distance):
        environment = self
        for _ in range(distance):
            environment = environment.enclosing

        return environment
