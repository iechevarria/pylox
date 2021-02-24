import expr as Expr
import stmt as Stmt
from token_type import TokenType as tt


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens, error_handler):
        self.tokens = tokens
        self.error_handler = error_handler
        self.current = 0

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    def declaration(self):
        try:
            if self.match(tt.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def statement(self):
        if self.match(tt.IF):
            return self.if_statement()
        if self.match(tt.PRINT):
            return self.print_statement()
        if self.match(tt.WHILE):
            return self.while_statement()
        if self.match(tt.LEFT_BRACE):
            return Stmt.Block(self.block())

        return self.expression_statement()

    def if_statement(self):
        self.consume(type=tt.LEFT_PAREN, message="Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(
            type=tt.RIGHT_PAREN, message="Expect ')' after if condition"
        )
        then_branch = self.statement()
        else_branch = self.statement() if self.match(tt.ELSE) else None
        return Stmt.If(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch
        )

    def print_statement(self):
        value = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(value)

    def var_declaration(self):
        name = self.consume(tt.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match(tt.EQUAL):
            initializer = self.expression()

        self.consume(tt.SEMICOLON, "Expect ';' after variable declaration")
        return Stmt.Var(name=name, initializer=initializer)

    def while_statement(self):
        self.consume(type=tt.LEFT_PAREN, message="Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(type=tt.RIGHT_PAREN, message="Expect ')' after condition.")
        body = self.statement()

        return Stmt.While(condition=condition, body=body)

    def expression_statement(self):
        expr = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after expression.")
        return Stmt.Expression(expr)

    def block(self):
        statements = []
        while (not self.check(tt.RIGHT_BRACE)) and (not self.is_at_end()):
            statements.append(self.declaration())

        self.consume(tt.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.or_()

        if self.match(tt.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Expr.Variable):
                return Expr.Assign(name=expr.name, value=value)

            self.error(token=equals, message="Invalid assignment target.")

        return expr

    def or_(self):
        expr = self.and_()

        while self.match(tt.OR):
            operator = self.previous()
            right = self.and_()
            expr = Expr.Logical(left=expr, operator=operator, right=right)
        
        return expr

    def and_(self):
        expr = self.equality()

        while self.match(tt.AND):
            operator = self.previous()
            right = self.and_()
            expr = Expr.Logical(left=expr, operator=operator, right=right)

        return expr

    def equality(self):
        expr = self.comparison()

        while self.match(tt.BANG_EQUAL, tt.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Expr.Binary(left=expr, operator=operator, right=right)

        return expr

    def comparison(self):
        expr = self.term()

        while self.match(tt.GREATER, tt.GREATER_EQUAL, tt.LESS, tt.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Expr.Binary(left=expr, operator=operator, right=right)

        return expr

    def term(self):
        expr = self.factor()

        while self.match(tt.MINUS, tt.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Expr.Binary(left=expr, operator=operator, right=right)

        return expr

    def factor(self):
        expr = self.unary()

        while self.match(tt.SLASH, tt.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(left=expr, operator=operator, right=right)

        return expr

    def unary(self):
        if self.match(tt.BANG, tt.MINUS):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)

        return self.primary()

    def primary(self):
        if self.match(tt.FALSE):
            return Expr.Literal(value=False)
        if self.match(tt.TRUE):
            return Expr.Literal(value=True)
        if self.match(tt.NIL):
            return Expr.Literal(value=None)

        if self.match(tt.NUMBER, tt.STRING):
            return Expr.Literal(self.previous().literal)

        if self.match(tt.IDENTIFIER):
            return Expr.Variable(self.previous())

        if self.match(tt.LEFT_PAREN):
            expr = self.expression()
            self.consume(tt.RIGHT_PAREN, "Expect ')' after expression.")
            return Expr.Grouping(expression=expr)

        raise self.error(token=self.peek(), message="Expect expression.")

    def match(self, *types):
        for t in types:
            if self.check(t):
                self.advance()
                return True

        return False

    def consume(self, type, message):
        if self.check(type):
            return self.advance()

        raise self.error(token=self.peek(), message=message)

    def error(self, token, message):
        self.error_handler.token_error(token=token, message=message)
        return ParseError()

    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if (self.previous().type == tt.SEMICOLON):
                return

            if self.peek().type in (
                tt.CLASS,
                tt.FUN,
                tt.VAR,
                tt.FOR,
                tt.IF,
                tt.WHILE,
                tt.PRINT,
                tt.RETURN
            ):
                return

            self.advance()

    def check(self, type):
        if self.is_at_end():
            return False

        return self.peek().type == type

    def advance(self):
        if not self.is_at_end():
            self.current += 1

        return self.previous()

    def is_at_end(self):
        return self.peek().type == tt.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]
