from .exceptions import Return, RuntimeException
from .environment import Environment

INIT = "init"


class LoxCallable:
    def call(self, interpreter, arguments):
        pass

    def arity(self):
        pass


class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure, is_initializer=False):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(
            declaration=self.declaration,
            closure=environment,
            is_initializer=self.is_initializer
        )

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)

        try:
            interpreter.execute_block(
                statements=self.declaration.body, environment=environment
            )
        except Return as r:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return r.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")

    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"


class LoxClass(LoxCallable):
    def __init__(self, name, superclass, methods):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def call(self, interpreter, arguments):
        instance = LoxInstance(self)
        intializer = self.find_method(name=INIT)
        if intializer is not None:
            intializer.bind(instance).call(
                interpreter=interpreter, arguments=arguments
            )
        return instance

    def arity(self):
        initializer = self.find_method(INIT)
        if initializer is None:
            return 0
        return initializer.arity()

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        if self.superclass is not None:
            return self.superclass.find_method(name)
        return None

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
            return method.bind(self)

        raise RuntimeException(
            token=name,
            message=f"Undefined property '{name.lexeme}'.",
        )

    def set(self, name, value):
        self.fields[name.lexeme] = value

    def __str__(self):
        return self.class_.name + " instance"
