from .exceptions import Return, RuntimeException
from .environment import Environment


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

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"


class LoxClass(LoxCallable):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def call(self, interpreter, arguments):
        return LoxInstance(self)

    def arity(self):
        return 0

    def find_method(self, name):
        return self.methods[name] if name in self.methods else None

    def __str__(self):
        return self.name


class LoxInstance:
    def __init__(self, class_):
        self.class_ = class_
        self.fields = {}

    def get(self, name):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.class_.find_method(name.lexeme)
        if method is not None:
            return method

        raise RuntimeException(
            token=name,
            message=f"Undefined property '{name.lexeme}'.",
        )

    def set(self, name, value):
        self.fields[name.lexeme] = value

    def __str__(self):
        return self.class_.name + " instance"
