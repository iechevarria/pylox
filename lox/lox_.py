import sys

from .error_handler import ErrorHandler
from .interpreter import Interpreter
from .parser_ import Parser
from .resolver import Resolver
from .scanner import Scanner


class Lox:
    def __init__(self, test=False):
        args = sys.argv

        self.error_handler = ErrorHandler()
        self.interpreter = Interpreter(error_handler=self.error_handler)

        # don't want to start a prompt when running tests
        if test:
            return
        elif (len(args) > 2):
            print("Usage: python lox [script]")
            sys.exit(64)
        elif (len(args) == 2):
            self.run_file(args[1])
        else:
            self.run_prompt()

    def run_file(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.run(f.read())

        if self.error_handler.had_error:
            sys.exit(65)
        if self.self.error_handler.had_runtime_error:
            sys.exit(70)

    def run_prompt(self):
        while True:
            try:
                line = input("> ")
            except EOFError:
                break
            self.run(line)
            # execute code even if previous statement had an error
            self.error_handler.had_error = False

    def run(self, source):
        scanner = Scanner(source=source, error_handler=self.error_handler)
        tokens = scanner.scan_tokens()

        parser = Parser(tokens=tokens, error_handler=self.error_handler)
        statements = parser.parse()

        # don't execute code that had parse errors
        if self.error_handler.had_error:
            return

        resolver = Resolver(interpreter=self.interpreter)
        resolver.resolve(*statements)

        # don't execute code that had resolution errors
        if self.error_handler.had_error:
            return

        self.interpreter.interperet(statements=statements)
