from .token_type import EOF


class ErrorHandler():
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False

    def scanner_error(self, line, message):
        """Error that occurs during scanning

        Separate from token_error because the scanner failed to create a token,
        so there's no token to pass
        """
        self.report(line=line, message=f"Error: {message}")

    def token_error(self, token, message):
        if token.type == EOF:
            self.report(line=token.line, message=f"Error at end: {message}")
        else:
            self.report(
                line=token.line,
                message=f"Error at '{token.lexeme}': {message}"
            )

    def report(self, line, message):
        print(f"[line {line}] {message}")
        self.had_error = True

    def runtime_error(self, error):
        print(error.message, f"[line {error.token.line}]")
        self.had_runtime_error = True
