from .token_ import Token
# I will freely admit this is dumb, but I'd rather not from x import *
from .token_type import (
    LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE, LEFT_BRACKET,
    RIGHT_BRACKET, COMMA, DOT, MINUS, PLUS, SEMICOLON, SLASH, STAR, BANG,
    BANG_EQUAL, EQUAL, EQUAL_EQUAL, GREATER, GREATER_EQUAL, LESS, LESS_EQUAL,
    IDENTIFIER, STRING, NUMBER, AND, CLASS, ELSE, FALSE, FUN, FOR, IF, NIL, OR,
    PRINT, RETURN, SUPER, THIS, TRUE, VAR, WHILE, EOF,
)


KEYWORDS = {
    "and": AND,
    "class": CLASS,
    "else": ELSE,
    "false": FALSE,
    "for": FOR,
    "fun": FUN,
    "if": IF,
    "nil": NIL,
    "or": OR,
    "print": PRINT,
    "return": RETURN,
    "super": SUPER,
    "this": THIS,
    "true": TRUE,
    "var": VAR,
    "while": WHILE,
}


def is_digit(char):
    return char >= "0" and char <= "9"


def is_alpha(char):
    return (
        (char >= "a" and char <= "z")
        or (char >= "A" and char <= "Z")
        or (char == "_")
    )


def is_alphanumeric(char):
    return is_digit(char) or is_alpha(char)


class Scanner:
    def __init__(self, source, error_handler):
        self.source = source
        self.error_handler = error_handler
        self.tokens = []

        self.start = 0
        self.current = 0
        self.line = 1

    def error(self, line, message):
        self.error_handler.scanner_error(line=line, message=message)

    def is_at_end(self):
        return self.current >= len(self.source)

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(
            Token(type=EOF, lexeme="", literal=None, line=self.line)
        )

        return self.tokens

    def scan_token(self):
        char = self.advance()

        # really wish PEP 636 was in for this part
        if char == "(":
            self.add_token(LEFT_PAREN)
        elif char == ")":
            self.add_token(RIGHT_PAREN)
        elif char == "{":
            self.add_token(LEFT_BRACE)
        elif char == "}":
            self.add_token(RIGHT_BRACE)
        elif char == "[":
            self.add_token(LEFT_BRACKET)
        elif char == "]":
            self.add_token(RIGHT_BRACKET)
        elif char == ",":
            self.add_token(COMMA)
        elif char == ".":
            self.add_token(DOT)
        elif char == "-":
            self.add_token(MINUS)
        elif char == "+":
            self.add_token(PLUS)
        elif char == ";":
            self.add_token(SEMICOLON)
        elif char == "*":
            self.add_token(STAR)

        # 1 or 2 token stuff
        elif char == "!":
            token = BANG_EQUAL if self.match("=") else BANG
            self.add_token(token)
        elif char == "=":
            token = EQUAL_EQUAL if self.match("=") else EQUAL
            self.add_token(token)
        elif char == "<":
            token = LESS_EQUAL if self.match("=") else LESS
            self.add_token(token)
        elif char == ">":
            token = GREATER_EQUAL if self.match("=") else GREATER
            self.add_token(token)

        # handle slash
        elif char == "/":
            if self.match('/'):
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            elif self.match('*'):
                self.block_comment()
            else:
                self.add_token(SLASH)

        # handle whitespace stuff
        elif char in [" ", "\r", "\t"]:
            return
        elif char == "\n":
            self.line += 1

        # handle string
        elif char == "\"":
            self.string()

        # handle other chars
        else:
            if is_digit(char):
                self.number()
            elif is_alpha(char):
                self.identifier()
            else:
                self.error(
                    line=self.line, message=f"Unexpected character: {char}"
                )

    def identifier(self):
        while (is_alphanumeric(self.peek())):
            self.advance()

        text = self.source[self.start:self.current]

        if text in KEYWORDS:
            self.add_token(KEYWORDS[text])
        else:
            self.add_token(IDENTIFIER)

    def number(self):
        while is_digit(self.peek()):
            self.advance()

        if self.peek() == '.' and is_digit(self.peek_next()):
            self.advance()
            while is_digit(self.peek()):
                self.advance()

        self.add_token_literal(
            type=NUMBER, literal=float(self.source[self.start:self.current])
        )

    def string(self):
        while self.peek() != "\"" and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if (self.is_at_end()):
            self.error(line=self.line, message="Unterminated string.")
            return

        # closing "
        self.advance()

        # trim surrounding quotes
        value = self.source[self.start + 1:self.current - 1]
        self.add_token_literal(type=STRING, literal=value)

    def block_comment(self):
        while (
            not (self.peek() == "*" and self.peek_next() == "/")
            and not self.is_at_end()
        ):
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.peek() == "*" and self.peek_next() == "/":
            self.advance(spaces=2)

    def match(self, expected):
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self):
        return "\0" if self.is_at_end() else self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def advance(self, spaces=1):
        self.current += spaces
        return self.source[self.current - 1]

    def add_token(self, type):
        self.add_token_literal(type, None)

    def add_token_literal(self, type, literal):
        text = self.source[self.start:self.current]
        self.tokens.append(
            Token(type=type, lexeme=text, literal=literal, line=self.line)
        )
