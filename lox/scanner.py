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

        self.token_strings = {
            "(": lambda: LEFT_PAREN,
            ")": lambda: RIGHT_PAREN,
            "{": lambda: LEFT_BRACE,
            "}": lambda: RIGHT_BRACE,
            "[": lambda: LEFT_BRACKET,
            "]": lambda: RIGHT_BRACKET,
            ",": lambda: COMMA,
            ".": lambda: DOT,
            "-": lambda: MINUS,
            "+": lambda: PLUS,
            ";": lambda: SEMICOLON,
            "*": lambda: STAR,
            "!": lambda: BANG_EQUAL if self.match("=") else BANG,
            "=": lambda: EQUAL_EQUAL if self.match("=") else EQUAL,
            "<": lambda: LESS_EQUAL if self.match("=") else LESS,
            ">": lambda: GREATER_EQUAL if self.match("=") else GREATER,
            "/": lambda: self.slash(),
            " ": lambda: None,
            "\r": lambda: None,
            "\t": lambda: None,
            "\n": lambda: self.newline(),
        }

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

        if char in self.token_strings:
            self.add_token(type=self.token_strings[char]())
        elif char == "\"":
            self.add_token(*self.string())
        elif is_digit(char):
            self.add_token(*self.number())
        elif is_alpha(char):
            self.add_token(type=self.identifier())
        else:
            self.error(
                line=self.line, message=f"Unexpected character: {char}"
            )

    # # #
    # # #   Specific token scanning functions
    # # #
    def string(self):
        while self.peek() != "\"" and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.error(line=self.line, message="Unterminated string.")
            return (None, None)

        # closing "
        self.advance()

        # trim surrounding quotes
        value = self.source[self.start + 1:self.current - 1]
        return (STRING, value)

    def slash(self):
        if self.match("/"):
            while self.peek() != "\n" and not self.is_at_end():
                self.advance()
            return None
        elif self.match("*"):
            return self.block_comment()
        else:
            return SLASH

    def block_comment(self):
        """Handles C-style block comments"""
        while (
            not (self.peek() == "*" and self.peek_next() == "/")
            and not self.is_at_end()
        ):
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.peek() == "*" and self.peek_next() == "/":
            self.advance(spaces=2)

        return None

    def newline(self):
        self.line += 1
        return None

    def identifier(self):
        while (is_alphanumeric(self.peek())):
            self.advance()

        text = self.source[self.start:self.current]

        if text in KEYWORDS:
            return KEYWORDS[text]
        else:
            return IDENTIFIER

    def number(self):
        while is_digit(self.peek()):
            self.advance()

        if self.peek() == '.' and is_digit(self.peek_next()):
            self.advance()
            while is_digit(self.peek()):
                self.advance()

        return (NUMBER, float(self.source[self.start:self.current]))

    # # #
    # # #   Utilities (mostly with side effects)
    # # #
    def add_token(self, type, literal=None):
        # handle empty tokens (whitespace, unterminated strings)
        if type is None:
            return

        text = self.source[self.start:self.current]
        self.tokens.append(
            Token(type=type, lexeme=text, literal=literal, line=self.line)
        )

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

    def is_at_end(self):
        return self.current >= len(self.source)

    def error(self, line, message):
        self.error_handler.scanner_error(line=line, message=message)
