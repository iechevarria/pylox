import sys

from ast_printer import print_ast
from error_handler import ErrorHandler
from interpreter import Interpreter
from parser_ import Parser
from scanner import Scanner


class Lox:
    def __init__(self):
        args = sys.argv

        self.error_handler = ErrorHandler()
        self.interpreter = Interpreter(error_handler=self.error_handler)

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

        if self.had_error():
            sys.exit(65)
        if self.had_runtime_error():
            sys.exit(70)


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

        parser = Parser(tokens=tokens, error_handler=self.error_handler)
        expression = parser.parse()

        if self.had_error():
            return

        print_ast(expression)
        self.interpreter.interperet(expression)


    def had_error(self):
        return self.error_handler.had_error


    def had_runtime_error(self):
        return self.error_handler.had_runtime_error


if __name__ == "__main__":
    Lox()
