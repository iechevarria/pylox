class ErrorHandler():
    def __init__(self):
        self.had_error = False


    def error(self, line, message):
        self.report(line, message)


    def report(self, line, message):
        print(f"[line {line}] Error: {message}")
        self.had_error = True
