from .callable_ import INIT

# constants for functions + classes
NONE = 0

# constants for function types
FUNCTION = 1
INITIALIZER = 2
METHOD = 3

# constants for class types
CLASS = 1
SUBCLASS = 2


class Resolver:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.error_handler = self.interpreter.error_handler
        self.current_function = NONE
        self.current_class = NONE
        self.scopes = []

    def resolve(self, *statements):
        resolvers = {
            # statements
            "Block": self.block,
            "Class": self.class_,
            "Expression": self.expression,
            "Function": self.function,
            "If": self.if_,
            "Print": self.print_,
            "Return": self.return_,
            "Var": self.var,
            "While": self.while_,

            # expressions
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
            "Unary": self.unary,
            "Variable": self.variable,
        }

        for statement in statements:
            resolvers[statement.__class__.__name__](statement)

    def resolve_function(self, function, type):
        enclosing_function = self.current_function
        self.current_function = type

        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve(*function.body)
        self.end_scope()
        self.current_function = enclosing_function

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name):
        if not self.scopes:
            return

        scope = self.scopes[-1]
        if name.lexeme in scope:
            self.error_handler.token_error(
                name, "Already variable with this name in this scope."
            )
        self.scopes[-1][name.lexeme] = False

    def define(self, name):
        if not self.scopes:
            return

        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr, name):
        for i, scope in reversed(list(enumerate(self.scopes))):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, (len(self.scopes) - 1 - i))
                return

    def block(self, stmt):
        self.begin_scope()
        self.resolve(*stmt.statements)
        self.end_scope()

    def class_(self, stmt):
        enclosing_class = self.current_class
        self.current_class = CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if (
            (stmt.superclass is not None)
            and (stmt.name.lexeme == stmt.superclass.name.lexeme)
        ):
            self.error_handler.token_error(
                token=stmt.superclass.name,
                message="A class can't inherit from itself."
            )

        if stmt.superclass is not None:
            self.current_class = SUBCLASS
            self.resolve(stmt.superclass)
            self.begin_scope()
            self.scopes[-1]["super"] = True

        self.begin_scope()
        self.scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = INITIALIZER if method.name.lexeme == INIT else METHOD
            self.resolve_function(function=method, type=declaration)

        self.end_scope()
        if stmt.superclass is not None:
            self.end_scope()

        self.current_class = enclosing_class

    def expression(self, stmt):
        self.resolve(stmt.expression)

    def function(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolve_function(function=stmt, type=FUNCTION)

    def if_(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)

    def print_(self, stmt):
        self.resolve(stmt.expression)

    def return_(self, stmt):
        if self.current_function == NONE:
            self.error_handler.token_error(
                stmt.keyword, "Can't return from top-level code."
            )
        if stmt.value is not None:
            if self.current_function == INITIALIZER:
                self.error_handler.token_error(
                    token=stmt.keyword,
                    message="Can't return a value from an initializer.",
                )

            self.resolve(stmt.value)

    def var(self, stmt):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    def while_(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def array(self, expr):
        for element in expr.values:
            self.resolve(element)

    def assign(self, expr):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)

    def binary(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def call(self, expr):
        self.resolve(expr.callee)
        for arg in expr.expressions:
            self.resolve(arg)

    def get(self, expr):
        self.resolve(expr.object)

    def grouping(self, expr):
        self.resolve(expr.expression)

    def literal(self, expr):
        return

    def logical(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def set_(self, expr):
        self.resolve(expr.value)
        self.resolve(expr.object)

    def super_(self, expr):
        if self.current_class == NONE:
            self.error_handler.token_error(
                token=expr.keyword,
                message="Can't use 'super' outside of a class."
            )
        elif self.current_class != SUBCLASS:
            self.error_handler.token_error(
                token=expr.keyword,
                message="Can't use 'super' in a class with no superclass."
            )

        self.resolve_local(expr=expr, name=expr.keyword)

    def this(self, expr):
        if self.current_class == NONE:
            self.error_handler.token_error(
                token=expr.keyword,
                message="Can't use 'this' outside of a class."
            )
        self.resolve_local(expr=expr, name=expr.keyword)

    def unary(self, expr):
        self.resolve(expr.right)

    def variable(self, expr):
        if (
            self.scopes and expr.name.lexeme in self.scopes[-1]
            and self.scopes[-1][expr.name.lexeme] is False
        ):
            self.error_handler.token_error(
                token=expr.name,
                message="Can't read local variable in its own initializer.",
            )

        self.resolve_local(expr=expr, name=expr.name)
