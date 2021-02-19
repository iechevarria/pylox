from lox import Lox
from token import Token
from token_type import TokenType as tt

class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []

        self.start = 0
        self.current = 0
        self.line = 1

        self.is_at_end = False
    

    def is_at_end(self):
        return current >= len(source)


    def scan_tokens(self):
        while not self.is_at_end():
            start = current
            scan_token()

        tokens.append(Token(tt.EOF, "", None, line))
        return tokens


    def _scan_token(self):
        char = self.advance()

        # really wish PEP 636 was in for this part

        # single token stuff
        single = self._add_single_char_token
        if char == "(":
            single(tt.LEFT_PAREN)
        elif char == ")":
            single(tt.RIGHT_PAREN)
        elif char == "{":
            single(tt.LEFT_BRACE)
        elif char == "}":
            single(tt.RIGHT_BRACE)
        elif char == ",":
            single(tt.COMMA)
        elif char == ".":
            single(tt.DOT)
        elif char == "-":
            single(tt.MINUS)
        elif char == "+":
            single(tt.PLUS)
        elif char == ";":
            single(tt.SEMICOLON)
        elif char == "*":
            single(tt.STAR)

        # 1 or 2 token stuff
        elif char == "!":
            token = tt.BANG_EQUAL if self._match("=") else tt.BANG
            single(token)
        elif char == "=":
            token = tt.EQUAL_EQUAL if self._match("=") else tt.EQUAL
            single(token)
    
        else:
            Lox.error(line, "Unexpected character.")


    def _match(self, expected):
        if self.is_at_end():
            return False
        if self.source[current] != expected:
            return False

        current += 1
        return True


    def _advance(self):
        self.current += 1
        return self.source[current - 1]
    

    def _add_single_char_token(self, type):
        self._add_token(type, None)


    def _add_token(self, type, literal):
        text = self.source[start:current]
        tokens.append(
            Token(type=type, text=text, literal=literal, line=self.line)
        )