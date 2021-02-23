from token_type import TokenType as tt


class RuntimeException(RuntimeError):
    def __init__(self, token, message):
        self.token = token
        self.message = message


def literal(expr):
    return expr.value


def grouping(expr):
    return evaluate(expr.expression)


def unary(expr):
    right = evaluate(expr.right)

    if expr.operator.type == tt.MINUS:
        check_number_operands(operator=expr.operator, operand=right)
        return - float(right)
    if expr.operator.type == tt.BANG:
        return not is_truthy(right)


def binary(expr):
    left = evaluate(expr.left)
    right = evaluate(expr.right)

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


def evaluate(expr):
    exprs = {
        "Binary": binary,
        "Grouping": grouping,
        "Literal": literal,
        "Unary": unary,
    }

    return exprs[expr.__class__.__name__](expr)


class Interpreter:
    def __init__(self, error_handler):
        self.error_handler = error_handler

    def interperet(self, expression):
        try:
            value = evaluate(expression)
            print(stringify(value))
        except RuntimeException as e:
            self.error_handler.runtime_error(e)


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
