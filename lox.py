import sys

from error_handler import ErrorHandler
from scanner import Scanner 


class Lox:
    def __init__(self):
        args = sys.argv

        self.error_handler = ErrorHandler()

        if (len(args) > 2):
            print("Usage: python lox [script]")
            sys.exit(64)
        elif (len(args) == 2):
            self.run_file(args[1])
        else:
            self.run_prompt()


    def run_file(self, path):
        with open(path, 'r') as f:
            self.run(f.read())

        if (self.error_handler.had_error):
            sys.exit(65)


    def run_prompt(self):
        while True:
            try:
                line = input("> ")
            except EOFError:
                break
            self.run(line)
            self.error_handler.had_error = False


    def run(self, source):
        scanner = Scanner(source=source, error_handler=self.error_handler)
        tokens = scanner.scan_tokens()

        for token in tokens:
            print(token)


if __name__ == "__main__":
    Lox()
