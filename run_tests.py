import io
import logging
import pathlib
import re
from contextlib import redirect_stdout

from lox import Lox


TOKEN_REGEX = re.compile(r"Error.*")
RUNTIME_REGEX = re.compile(r"(?<=expect runtime error:\s).*")

OUTPUT = "output"
TOKEN_ERROR = "token"
RUNTIME_ERROR = "runtime"


def run_test(test, verbose=True):
    with open(test, "r", encoding="utf-8") as f:
        source = f.read()

    # get expected output if exists
    expected = "\n".join([
        line.split("// expect: ")[1] for line in source.split("\n")
        if "// expect:" in line
    ])

    # use this to change acceptance conditions
    expected_type = OUTPUT

    # get token error if exists
    if not expected:
        for line in source.split("\n"):
            search = TOKEN_REGEX.search(line)
            if search:
                expected_type = TOKEN_ERROR
                expected += search.group(0).strip() + "\n"

    # get runtime error
    if not expected:
        for line in source.split("\n"):
            search = RUNTIME_REGEX.search(line)
            if search:
                expected_type = RUNTIME_ERROR
                expected += search.group(0).strip() + "\n"

    # actually run the thing
    captured_stdout = io.StringIO()
    with redirect_stdout(captured_stdout):
        Lox(test=True).run(source=source)

    # process + compare output to expected
    actual = captured_stdout.getvalue()[:-1]
    if expected_type == TOKEN_ERROR:
        actual = "\n".join([
            TOKEN_REGEX.search(line).group(0).strip()
            for line in actual.split("\n")
        ])
    if expected_type == RUNTIME_ERROR:
        actual = "\n".join([
            actual.split("[")[0].strip() for line in actual.split("\n")
        ])

    if actual.strip() == expected.strip():
        return 1
    else:
        print(f"{test} failed")
        if verbose:
            print(f"Expected:\n{expected}\n")
            print(f"Actual:\n{actual}\n\n")
        return 0


def run_tests(dir_):
    passes = 0
    tests = list(pathlib.Path(dir_).glob("*/*.lox"))
    for test in tests:
        try:
            passes += run_test(test, verbose=True)
        except Exception:
            print(logging.exception(f"\nException on {test}"))

    print(f"{passes} / {len(tests)} tests passed")


if __name__ == "__main__":
    run_tests("test")
