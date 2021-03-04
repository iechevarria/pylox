from . import expr as Expr
from . import stmt as Stmt
# yeah this is dumb but I don't like doing "from x import *"
from .token_type import (
    LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE, LEFT_BRACKET,
    RIGHT_BRACKET, COMMA, DOT, MINUS, PLUS, SEMICOLON, SLASH, STAR, BANG,
    BANG_EQUAL, EQUAL, EQUAL_EQUAL, GREATER, GREATER_EQUAL, LESS, LESS_EQUAL,
    IDENTIFIER, STRING, NUMBER, AND, CLASS, ELSE, FALSE, FUN, FOR, IF, NIL, OR,
    PRINT, RETURN, SUPER, THIS, TRUE, VAR, WHILE, EOF,
)


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

    # # #
    # # #   Declarations
    # # #
    def declaration(self):
        try:
            if self.match(CLASS):
                return self.class_declaration()
            if self.match(FUN):
                return self.function("function")
            if self.match(VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def class_declaration(self):
        name = self.consume(type=IDENTIFIER, message="Expect class name.")

        superclass = None
        if self.match(LESS):
            self.consume(type=IDENTIFIER, message="Expect superclass name.")
            superclass = Expr.Variable(self.previous())

        self.consume(type=LEFT_BRACE, message="Expect '{' before class body.")

        methods = []
        while not self.check(type=RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))

        self.consume(type=RIGHT_BRACE, message="Expect '}' after class body.")

        return Stmt.Class(name=name, superclass=superclass, methods=methods)

    def function(self, kind):
        name = self.consume(type=IDENTIFIER, message=f"Expect {kind} name.")
        self.consume(
            type=LEFT_PAREN, message=f"Expect '(' after {kind} name."
        )
        parameters = []
        if not self.check(type=RIGHT_PAREN):
            condition = True
            while condition:
                if len(parameters) >= 255:
                    self.error(
                        token=self.peek(),
                        message="Can't have more than 255 parameters."
                    )
                parameters.append(self.consume(
                    type=IDENTIFIER, message="Expect parameter name."
                ))
                condition = self.match(COMMA)

        self.consume(
            type=RIGHT_PAREN, message="Expect ')' after parameters."
        )
        self.consume(
            type=LEFT_BRACE, message=f"Expect '{{' before {kind} body."
        )
        body = self.block()
        return Stmt.Function(name=name, params=parameters, body=body)

    def var_declaration(self):
        name = self.consume(type=IDENTIFIER, message="Expect variable name.")

        initializer = None
        if self.match(EQUAL):
            initializer = self.expression()

        self.consume(SEMICOLON, "Expect ';' after variable declaration")
        return Stmt.Var(name=name, initializer=initializer)

    # # #
    # # #   Statements
    # # #
    def statement(self):
        if self.match(FOR):
            return self.for_statement()
        if self.match(IF):
            return self.if_statement()
        if self.match(PRINT):
            return self.print_statement()
        if self.match(RETURN):
            return self.return_statement()
        if self.match(WHILE):
            return self.while_statement()
        if self.match(LEFT_BRACE):
            return Stmt.Block(self.block())

        return self.expression_statement()

    def for_statement(self):
        """Desugars for statement and turns it into a while statement"""
        self.consume(type=LEFT_PAREN, message="Excpect '(' after 'for'.")

        if self.match(SEMICOLON):
            initializer = None
        elif self.match(VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = (
            self.expression() if not self.check(type=SEMICOLON) else None
        )
        self.consume(
            type=SEMICOLON, message="Expect ';' after loop condition."
        )

        increment = (
            self.expression() if not self.check(type=RIGHT_PAREN) else None
        )
        self.consume(
            type=RIGHT_PAREN, message="Expect ')' after for clause."
        )

        body = self.statement()

        # take for loop statements and desugar them into a while loop
        if increment is not None:
            body = Stmt.Block(statements=[body, Stmt.Expression(increment)])

        condition = (
            Expr.Literal(value=True) if condition is None else condition
        )
        body = Stmt.While(condition=condition, body=body)

        if initializer is not None:
            body = Stmt.Block(statements=[initializer, body])

        return body

    def if_statement(self):
        self.consume(type=LEFT_PAREN, message="Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(
            type=RIGHT_PAREN, message="Expect ')' after if condition"
        )
        then_branch = self.statement()
        else_branch = self.statement() if self.match(ELSE) else None
        return Stmt.If(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch
        )

    def print_statement(self):
        value = self.expression()
        self.consume(type=SEMICOLON, message="Expect ';' after value.")
        return Stmt.Print(value)

    def return_statement(self):
        keyword = self.previous()
        value = self.expression() if not self.check(type=SEMICOLON) else None

        self.consume(
            type=SEMICOLON, message="Expect ';' after return value"
        )
        return Stmt.Return(keyword=keyword, value=value)

    def while_statement(self):
        self.consume(type=LEFT_PAREN, message="Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(
            type=RIGHT_PAREN, message="Expect ')' after condition."
        )
        body = self.statement()

        return Stmt.While(condition=condition, body=body)

    def block(self):
        statements = []
        while (not self.check(type=RIGHT_BRACE)) and (not self.is_at_end()):
            statements.append(self.declaration())

        self.consume(type=RIGHT_BRACE, message="Expect '}' after block.")
        return statements

    def expression_statement(self):
        expr = self.expression()
        self.consume(type=SEMICOLON, message="Expect ';' after expression.")
        return Stmt.Expression(expr)

    # # #
    # # #   Expressions
    # # #
    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.or_()

        if self.match(EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Expr.Variable):
                return Expr.Assign(name=expr.name, value=value)
            elif isinstance(expr, Expr.Get):
                return Expr.Set(
                    object=expr.object, name=expr.name, value=value
                )

            self.error(token=equals, message="Invalid assignment target.")

        return expr

    def or_(self):
        expr = self.and_()

        while self.match(OR):
            operator = self.previous()
            right = self.and_()
            expr = Expr.Logical(left=expr, operator=operator, right=right)

        return expr

    def and_(self):
        expr = self.equality()

        while self.match(AND):
            operator = self.previous()
            right = self.and_()
            expr = Expr.Logical(left=expr, operator=operator, right=right)

        return expr

    def equality(self):
        expr = self.comparison()

        while self.match(BANG_EQUAL, EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Expr.Binary(left=expr, operator=operator, right=right)

        return expr

    def comparison(self):
        expr = self.term()

        while self.match(GREATER, GREATER_EQUAL, LESS, LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Expr.Binary(left=expr, operator=operator, right=right)

        return expr

    def term(self):
        expr = self.factor()

        while self.match(MINUS, PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Expr.Binary(left=expr, operator=operator, right=right)

        return expr

    def factor(self):
        expr = self.unary()

        while self.match(SLASH, STAR):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(left=expr, operator=operator, right=right)

        return expr

    def unary(self):
        if self.match(BANG, MINUS):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)

        return self.call()

    def call(self):
        expr = self.primary()

        while (True):
            if self.match(LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(DOT):
                name = self.consume(
                    type=IDENTIFIER,
                    message="Expect property name after '.'."
                )
                expr = Expr.Get(object=expr, name=name)
            else:
                break

        return expr

    def finish_call(self, callee):
        arguments = []
        if not self.check(type=RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(COMMA):
                arguments.append(self.expression())
                if len(arguments) > 255:
                    self.error(
                        token=self.previous(),
                        message="Can't have more than 255 arguments."
                    )

        paren = self.consume(
            type=RIGHT_PAREN, message="Expect ')' after arguments."
        )

        # convert arguments to tuple so returned Call is hashable
        return Expr.Call(
            callee=callee, paren=paren, expressions=tuple(arguments)
        )

    def primary(self):
        # array creation
        if self.match(LEFT_BRACKET):
            elements = []
            if not self.check(type=RIGHT_BRACKET):
                elements.append(self.expression())
                while self.match(COMMA):
                    elements.append(self.expression())
            self.consume(
                type=RIGHT_BRACKET, message="Expect ']' after array creation"
            )
            return Expr.Array(values=elements)

        if self.match(FALSE):
            return Expr.Literal(value=False)
        if self.match(TRUE):
            return Expr.Literal(value=True)
        if self.match(NIL):
            return Expr.Literal(value=None)

        if self.match(NUMBER, STRING):
            return Expr.Literal(self.previous().literal)

        if self.match(SUPER):
            keyword = self.previous()
            self.consume(type=DOT, message="Expect '.' after 'super'.")
            method = self.consume(
                type=IDENTIFIER, message="Expect superclass method name."
            )
            return Expr.Super(keyword=keyword, method=method)

        if self.match(THIS):
            return Expr.This(self.previous())

        if self.match(IDENTIFIER):
            return Expr.Variable(self.previous())

        if self.match(LEFT_PAREN):
            expr = self.expression()
            self.consume(
                type=RIGHT_PAREN, message="Expect ')' after expression."
            )
            return Expr.Grouping(expression=expr)

        raise self.error(token=self.peek(), message="Expect expression.")

    # # #
    # # #   Utilities
    # # #
    def synchronize(self):
        """Recover from error so that more errors can be found"""
        self.advance()

        while not self.is_at_end():
            if (self.previous().type == SEMICOLON):
                return

            if self.peek().type in (
                CLASS,
                FUN,
                VAR,
                FOR,
                IF,
                WHILE,
                PRINT,
                RETURN,
            ):
                return

            self.advance()

    def match(self, *types):
        for t in types:
            if self.check(type=t):
                self.advance()
                return True

        return False

    def consume(self, type, message):
        if self.check(type=type):
            return self.advance()

        raise self.error(token=self.peek(), message=message)

    def error(self, token, message):
        self.error_handler.token_error(token=token, message=message)
        return ParseError()

    def check(self, type):
        if self.is_at_end():
            return False

        return self.peek().type == type

    def advance(self):
        if not self.is_at_end():
            self.current += 1

        return self.previous()

    def is_at_end(self):
        return self.peek().type == EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]
