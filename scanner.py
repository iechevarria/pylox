from token import Token
from token_type import TokenType as tt


KEYWORDS = {
    "and": tt.AND,
    "class": tt.CLASS,
    "else": tt.ELSE,
    "false": tt.FALSE,
    "for": tt.FOR,
    "fun": tt.FUN,
    "if": tt.IF,
    "nil": tt.NIL,
    "or": tt.OR,
    "print": tt.PRINT,
    "return": tt.RETURN,
    "super": tt.SUPER,
    "this": tt.THIS,
    "true": tt.TRUE,
    "var": tt.VAR,
    "while": tt.WHILE,
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
        self.error_handler.error(line=line, message=message)


    def is_at_end(self):
        return self.current >= len(self.source)


    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(
            Token(type=tt.EOF, lexeme="", literal=None, line=self.line)
        )

        return self.tokens


    def scan_token(self):
        char = self.advance()

        # really wish PEP 636 was in for this part
        if char == "(":
            self.add_token(tt.LEFT_PAREN)
        elif char == ")":
            self.add_token(tt.RIGHT_PAREN)
        elif char == "{":
            self.add_token(tt.LEFT_BRACE)
        elif char == "}":
            self.add_token(tt.RIGHT_BRACE)
        elif char == ",":
            self.add_token(tt.COMMA)
        elif char == ".":
            self.add_token(tt.DOT)
        elif char == "-":
            self.add_token(tt.MINUS)
        elif char == "+":
            self.add_token(tt.PLUS)
        elif char == ";":
            self.add_token(tt.SEMICOLON)
        elif char == "*":
            self.add_token(tt.STAR)

        # 1 or 2 token stuff 
        elif char == "!":
            token = tt.BANG_EQUAL if self.match("=") else tt.BANG
            self.add_token(token)
        elif char == "=":
            token = tt.EQUAL_EQUAL if self.match("=") else tt.EQUAL
            self.add_token(token)
        elif char == "<":
            token = tt.LESS_EQUAL if self.match("=") else tt.LESS
            self.add_token(token)
        elif char == ">":
            token = tt.GREATER_EQUAL if self.match("=") else tt.GREATER
        
        # handle slash
        elif char == "/":
            if self.match('/'):
                while (self.peek() != "\n" and not self.is_at_end()):
                    self.advance()
            else:
                self.add_token(tt.SLASH)

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
                self.error(self.line, f"Unexpected character: {char}")


    def identifier(self):
        while (is_alphanumeric(self.peek())):
            self.advance()

        text = self.source[self.start:self.current]

        if text in KEYWORDS:
            self.add_token(KEYWORDS[text])
        else:
            self.add_token(tt.IDENTIFIER)


    def number(self):
        while is_digit(self.peek()):
            self.advance()

        if self.peek() == '.' and is_digit(self.peek_next()):
            self.advance()
            while is_digit(self.peek()):
                self.advance()

        self.add_token_literal(
            type=tt.NUMBER, literal=float(self.source[self.start:self.current])
        )


    def string(self):
        while self.peek() != "\"" and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()
        
        if (self.is_at_end()):
            self.error(self.line, "Unterminated string.")
            return

        # closing "
        self.advance()

        # trim surrounding quotes
        value = self.source[self.start + 1:self.current - 1]
        self.add_token_literal(type=tt.STRING, literal=value)


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


    def advance(self):
        self.current += 1
        return self.source[self.current - 1]
    

    def add_token(self, type):
        self.add_token_literal(type, None)


    def add_token_literal(self, type, literal):
        text = self.source[self.start:self.current]
        self.tokens.append(
            Token(type=type, lexeme=text, literal=literal, line=self.line)
        )
