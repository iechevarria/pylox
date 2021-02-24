from environment import Environment
from errors import RuntimeException
from token_type import TokenType as tt


class Interpreter:
    def __init__(self, error_handler):
        self.error_handler = error_handler
        self.environment = Environment()

    def interperet(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeException as e:
            self.error_handler.runtime_error(e)

    def execute(self, stmt):
        stmts = {
            "Expression": self.expression,
            "Print": self.print_,
            "Var": self.var,
        }
        return stmts[stmt.__class__.__name__](stmt)

    def evaluate(self, expr):
        exprs = {
            "Assign": self.assign,
            "Binary": self.binary,
            "Grouping": self.grouping,
            "Literal": self.literal,
            "Unary": self.unary,
            "Variable": self.variable,
        }

        return exprs[expr.__class__.__name__](expr)

    def expression(self, stmt):
        self.evaluate(stmt.expression)

    def literal(self, expr):
        return expr.value

    def grouping(self, expr):
        return self.evaluate(expr.expression)

    def unary(self, expr):
        right = self.evaluate(expr.right)

        if expr.operator.type == tt.MINUS:
            check_number_operands(operator=expr.operator, operand=right)
            return - float(right)
        if expr.operator.type == tt.BANG:
            return not is_truthy(right)

    def binary(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.type == tt.GREATER:
            check_number_operands(expr.operator, left, right)
            return left > right
        if expr.operator.type == tt.GREATER_EQUAL:
            check_number_operands(expr.operator, left, right)
            return left >= right
        if expr.operator.type == tt.LESS:
            check_number_operands(expr.operator, left, right)
            return left < right
        if expr.operator.type == tt.LESS_EQUAL:
            check_number_operands(expr.operator, left, right)
            return left <= right
        if expr.operator.type == tt.BANG_EQUAL:
            return not is_equal(a=left, b=right)
        if expr.operator.type == tt.EQUAL_EQUAL:
            return is_equal(a=left, b=right)
        if expr.operator.type == tt.MINUS:
            check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        if expr.operator.type == tt.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            elif isinstance(left, str) or isinstance(right, str):
                return stringify(left) + stringify(right)
            raise RuntimeException(
                token=expr.operator,
                message="Operands must be two numbers or two strings.",
            )
        if expr.operator.type == tt.SLASH:
            check_number_operands(expr.operator, left, right)
            if right == 0.0:
                raise RuntimeException(
                    token=expr.operator,
                    message="Division by zero error.",
                )
            return float(left) / float(right)
        if expr.operator.type == tt.STAR:
            check_number_operands(expr.operator, left, right)
            return float(left) * float(right)

    def variable(self, expr):
        return self.environment.get(expr.name)

    def print_(self, stmt):
        value = self.evaluate(stmt.expression)
        print(stringify(value))

    def var(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(name=stmt.name.lexeme, value=value)

    def assign(self, expr):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value


def check_number_operands(operator, *operands):
    if all(isinstance(operand, float) for operand in operands):
        return
    raise RuntimeException(token=operator, message="Operand must be a number.")


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

    return str(obj)


def is_truthy(obj):
    if obj is None:
        return False
    if isinstance(obj, bool):
        return obj

    return True


def is_equal(a, b):
    if (a is None and b is None):
        return True
    if (a is None):
        return False

    return a == b
