from .token_type import TokenType as tt


class ErrorHandler():
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False

    def error(self, line, message):
        self.report(line=line, message=message)

    def token_error(self, token, message):
        if token.type == tt.EOF:
            self.report(line=token.line, message=f" at end {message}")
        else:
            self.report(
                line=token.line,
                message=f" at '{token.lexeme}' {message}"
            )

    def runtime_error(self, error):
        print(error.message, f"[line {error.token.line}]")
        self.had_runtime_error = True

    def report(self, line, message):
        print(f"[line {line}] Error: {message}")
        self.had_error = True
