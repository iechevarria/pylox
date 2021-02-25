from exceptions import Return
from environment import Environment


class LoxCallable:
    def call(self, interpreter, arguments):
        pass

    def arity(self):
        pass


class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        [
            environment.define(param.lexeme, arg)
            for param, arg in zip(self.declaration.params, arguments)
        ]

        try:
            interpreter.execute_block(
                statements=self.declaration.body, environment=environment
            )
        except Return as r:
            return r.value

    def arity(self):
        return len(self.declaration.params)

    def to_string(self):
        return f"<fn {self.declaration.name.lexeme}>"
