from time import time

from .exceptions import Return, RuntimeException
from .environment import Environment

INIT = "init"


# simplifies checking if a variable is callable in the interpreter
class LoxCallable:
    pass


class Clock(LoxCallable):
    """Built-in function to get time"""
    def __init__(self):
        pass

    def arity(self):
        return 0

    def call(self, interpreter, arguments):
        return time()

    def __str__(self):
        return "<native fn>"


class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure, is_initializer=False):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def bind(self, instance):
        """Binds an instance to a method so that the it can be used like so:

        > class Person { print_name() { print this.name; }}
        > var jim = Person();
        > jim.name = "Jim";
        > var fn = jim.print_name;
        > fn()
        Jim
        """
        environment = Environment(enclosing=self.closure)
        environment.define(name="this", value=instance)
        return LoxFunction(
            declaration=self.declaration,
            closure=environment,
            is_initializer=self.is_initializer,
        )

    def call(self, interpreter, arguments):
        # define args in environment so they can be used while executing block
        environment = Environment(enclosing=self.closure)
        # don't need to check that the correct number of args are passed in -
        # already checked in the interpreter
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(name=param.lexeme, value=arg)

        try:
            interpreter.execute_block(
                statements=self.declaration.body, environment=environment
            )
        except Return as r:
            # always return instance when initializer is called, even if return
            # is explicitly called
            if self.is_initializer:
                return self.closure.get_at(distance=0, name="this")
            return r.value

        if self.is_initializer:
            return self.closure.get_at(distance=0, name="this")

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
        instance = LoxInstance(class_=self)
        intializer = self.find_method(name=INIT)
        if intializer is not None:
            intializer.bind(instance=instance).call(
                interpreter=interpreter, arguments=arguments
            )
        return instance

    def arity(self):
        initializer = self.find_method(name=INIT)
        if initializer is None:
            return 0
        return initializer.arity()

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        # traverse the inheritance hierarchy to find method
        if self.superclass is not None:
            return self.superclass.find_method(name=name)
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

        # bind instance to method
        method = self.class_.find_method(name=name.lexeme)
        if method is not None:
            return method.bind(instance=self)

        raise RuntimeException(
            token=name,
            message=f"Undefined property '{name.lexeme}'.",
        )

    def set(self, name, value):
        self.fields[name.lexeme] = value

    def __str__(self):
        return self.class_.name + " instance"
