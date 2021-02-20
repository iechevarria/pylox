def binary_str(expr):
    return parenthesize(
        name=expr.operator.lexeme,
        exprs=[expr.left, expr.right]
    )


def grouping_str(expr):
    return parenthesize(name="group", exprs=[expr.expression])


def literal_str(expr):
    if expr.value is None:
        return "nil"
    return str(expr.value)


def unary_str(expr):
    return parenthesize(
        name=expr.operator.lexeme, exprs=[expr.right]
    )


EXPRS = {
    "Binary": binary_str,
    "Grouping": grouping_str,
    "Literal": literal_str,
    "Unary": unary_str,
}


def parenthesize(name, exprs):
    out = "(" + name
    for e in exprs:
        out += " "
        out += EXPRS[e.__class__.__name__](e)
    out += ")"

    return out


def print_ast(expr):
    print(EXPRS[expr.__class__.__name__](expr))



if __name__ == "__main__":
    import expr
    from token import Token
    from token_type import TokenType as tt
    
    # test printing
    expression = expr.Binary(
        expr.Unary(
            Token(type=tt.MINUS, lexeme="-", literal=None, line=1),
            expr.Literal(123),
        ),
        Token(type=tt.STAR, lexeme="*", literal=None, line=1),
        expr.Grouping(
            expr.Literal(45.67)
        ),
    )

    print_ast(expression)
