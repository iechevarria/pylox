import sys


class Lox:
    had_error = False

    def __init__(self):
        args = sys.argv
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

        if (Lox.had_error):
            sys.exit(65)


    def run_prompt(self):
        while True:
            try:
                line = input("> ")
            except EOFError:
                break
            self.run(line)
            Lox.had_error = False


    def run(self, source):
        # Scanner scanner = new Scanner(source);
        # List<Token> tokens = scanner.scanTokens();
        tokens = source.split(" ")

        for token in tokens:
            print(token)


    @staticmethod
    def error(line, message):
        Lox._report(line, message)


    @staticmethod
    def _report(line, message):
        print(f"[line {line}] Error: {message}")
        Lox.had_error = True


if __name__ == "__main__":
    Lox()
