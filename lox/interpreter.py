from .callable_ import (
    Clock, INIT, LoxCallable, LoxClass, LoxFunction, LoxInstance
)
from .environment import Environment
from .exceptions import Return, RuntimeException
from .token_type import *


class Interpreter:
    def __init__(self, error_handler):
        self.error_handler = error_handler
        self.globals = Environment()

        # add built-in function clock to all interpreters
        self.globals.define(name="clock", value=Clock())

        self.environment = self.globals

        # dict that contains an identifier and the depth at which it is defined
        # example: {"foo": 4, "bar": 1}
        self.locals = {}

    def interperet(self, statements):
        try:
            for statement in statements:
                self.execute(stmt=statement)
        except RuntimeException as e:
            self.error_handler.runtime_error(error=e)

    def resolve(self, expr, depth):
        """Called only by Resolver on pass before actual interpretation"""
        self.locals[expr] = depth

    def execute(self, stmt):
        stmts = {
            "Block": self.block,
            "Class": self.class_,
            "Expression": self.expression,
            "Function": self.function,
            "If": self.if_,
            "Print": self.print_,
            "Return": self.return_,
            "Var": self.var,
            "While": self.while_,
        }
        return stmts[stmt.__class__.__name__](stmt)

    def block(self, stmt):
        """Creates new scope for block locals"""
        self.execute_block(
            statements=stmt.statements,
            environment=Environment(enclosing=self.environment)
        )

    def execute_block(self, statements, environment):
        # keep track of old scope so we can return to it easily
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(stmt=statement)
        finally:
            # exit scope
            self.environment = previous

    def class_(self, stmt):
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(expr=stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeException(
                    token=stmt.superclass.name,
                    message="Superclass must be a class."
                )

        self.environment.define(name=stmt.name.lexeme, value=None)

        # create new scope inside class to define "super" - used for the
        # closure for the methods below
        if superclass is not None:
            self.environment = Environment(enclosing=self.environment)
            self.environment.define(name="super", value=superclass)

        methods = {
            method.name.lexeme: LoxFunction(
                declaration=method,
                closure=self.environment,
                is_initializer=(method.name.lexeme == INIT),
            ) for method in stmt.methods
        }

        class_ = LoxClass(
            name=stmt.name.lexeme, superclass=superclass, methods=methods
        )

        # get out of scope created to define super above
        if superclass is not None:
            self.environment = self.environment.enclosing

        self.environment.assign(name=stmt.name, value=class_)

    def expression(self, stmt):
        self.evaluate(expr=stmt.expression)

    def function(self, stmt):
        function = LoxFunction(declaration=stmt, closure=self.environment)
        self.environment.define(name=stmt.name.lexeme, value=function)

    def if_(self, stmt):
        if is_truthy(self.evaluate(expr=stmt.condition)):
            self.execute(stmt=stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt=stmt.else_branch)

    def print_(self, stmt):
        value = self.evaluate(expr=stmt.expression)
        print(stringify(obj=value))

    def return_(self, stmt):
        value = None
        if stmt.value is not None:
            value = self.evaluate(expr=stmt.value)
        # Return is an exception. It's convenient to use exceptional control
        # flow to immediately bring the return value back
        raise Return(value)

    def var(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(name=stmt.name.lexeme, value=value)

    def while_(self, stmt):
        while is_truthy(self.evaluate(expr=stmt.condition)):
            self.execute(stmt=stmt.body)

    def evaluate(self, expr):
        exprs = {
            "Array": self.array,
            "Assign": self.assign,
            "Binary": self.binary,
            "Call": self.call,
            "Get": self.get,
            "Grouping": self.grouping,
            "Literal": self.literal,
            "Logical": self.logical,
            "Set": self.set_,
            "Super": self.super_,
            "This": self.this,
            "Unary": self.unary,
            "Variable": self.variable,
        }
        return exprs[expr.__class__.__name__](expr)

    def array(self, expr):
        """bonus expression not included in Lox spec"""
        return [self.evaluate(element) for element in expr.values]

    def assign(self, expr):
        value = self.evaluate(expr=expr.value)

        # use resolver to find where a name is defined, otherwise assign to
        # globals
        if expr in self.locals:
            self.environment.assign_at(
                distance=self.locals[expr], name=expr.name, value=value
            )
        else:
            self.globals.assign(name=expr.name, value=value)

        return value

    def binary(self, expr):
        left = self.evaluate(expr=expr.left)
        right = self.evaluate(expr=expr.right)

        if expr.operator.type == GREATER:
            check_number_operands(expr.operator, left, right)
            return left > right
        if expr.operator.type == GREATER_EQUAL:
            check_number_operands(expr.operator, left, right)
            return left >= right
        if expr.operator.type == LESS:
            check_number_operands(expr.operator, left, right)
            return left < right
        if expr.operator.type == LESS_EQUAL:
            check_number_operands(expr.operator, left, right)
            return left <= right
        if expr.operator.type == BANG_EQUAL:
            return not is_equal(a=left, b=right)
        if expr.operator.type == EQUAL_EQUAL:
            return is_equal(a=left, b=right)
        if expr.operator.type == MINUS:
            check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        if expr.operator.type == PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeException(
                token=expr.operator,
                message="Operands must be two numbers or two strings.",
            )
        if expr.operator.type == SLASH:
            check_number_operands(expr.operator, left, right)
            if right == 0.0:
                raise RuntimeException(
                    token=expr.operator,
                    message="Division by zero error.",
                )
            return float(left) / float(right)
        if expr.operator.type == STAR:
            check_number_operands(expr.operator, left, right)
            return float(left) * float(right)

    def call(self, expr):
        """Calls a callable after checking number of params = number of args"""
        callee = self.evaluate(expr=expr.callee)

        if not isinstance(callee, LoxCallable):
            raise RuntimeException(
                token=expr.paren,
                message="Can only call functions and classes."
            )

        arguments = [self.evaluate(arg) for arg in expr.expressions]

        if len(arguments) != callee.arity():
            raise RuntimeException(
                token=expr.paren,
                message=f"Expected {callee.arity()} arguments but got {len(arguments)}."  # noqa: E501
            )

        return callee.call(interpreter=self, arguments=arguments)

    def literal(self, expr):
        return expr.value

    def logical(self, expr):
        left = self.evaluate(expr.left)

        if expr.operator.type == OR:
            if is_truthy(left):
                return left
        else:
            if not is_truthy(left):
                return left

        return self.evaluate(expr.right)

    def set_(self, expr):
        obj = self.evaluate(expr.object)

        if not isinstance(obj, LoxInstance):
            raise RuntimeException(
                token=expr.name, message="Only instances have fields."
            )

        value = self.evaluate(expr.value)
        obj.set(name=expr.name, value=value)
        return value

    def super_(self, expr):
        distance = self.locals[expr]
        superclass = self.environment.get_at(distance=distance, name="super")
        # a bit of a hack to get the instance itself
        obj = self.environment.get_at(distance=distance - 1, name="this")
        method = superclass.find_method(name=expr.method.lexeme)

        if method is None:
            raise RuntimeException(
                token=expr.method,
                message=f"Undefined property '{expr.method.lexeme}'.",
            )

        return method.bind(obj)

    def this(self, expr):
        return self.look_up_variable(name=expr.keyword, expr=expr)

    def grouping(self, expr):
        return self.evaluate(expr.expression)

    def unary(self, expr):
        right = self.evaluate(expr.right)

        if expr.operator.type == MINUS:
            check_number_operands(expr.operator, right)
            return - float(right)
        if expr.operator.type == BANG:
            return not is_truthy(right)

    def get(self, expr):
        obj = self.evaluate(expr.object)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)

        raise RuntimeException(
            token=expr.name, message="Only instances have properties."
        )

    def variable(self, expr):
        return self.look_up_variable(expr.name, expr)

    def look_up_variable(self, name, expr):
        if expr in self.locals:
            return self.environment.get_at(self.locals[expr], name.lexeme)
        return self.globals.get(name)


def check_number_operands(operator, *operands):
    if all(isinstance(operand, float) for operand in operands):
        return

    message = (
        "Operands must be numbers." if len(operands) > 1
        else "Operand must be a number."
    )
    raise RuntimeException(token=operator, message=message)


def stringify(obj):
    if obj is None:
        return "nil"

    if isinstance(obj, float):
        text = str(obj)
        if text.endswith(".0"):
            text = text[:-2]
        return text

    if isinstance(obj, bool):
        return str(obj).lower()

    if isinstance(obj, list):
        return "[" + ", ".join([stringify(e) for e in obj]) + "]"

    return str(obj)


def is_truthy(obj):
    if obj is None:
        return False
    if isinstance(obj, bool):
        return obj

    return True


def is_equal(a, b):
    if a is None and b is None:
        return True
    if a is None:
        return False
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b

    return a == b
