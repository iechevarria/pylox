import os
import io
from contextlib import redirect_stdout
import logging
import pathlib

from lox import Lox


def run_test(test, verbose=True):
    with open(test, "r", encoding="utf-8") as f:
        source = f.read()

    expected = "\n".join([
        line.split("// expect: ")[1] for line in source.split("\n") 
        if "// expect:" in line
    ])

    captured_stdout = io.StringIO()
    with redirect_stdout(captured_stdout):
        Lox(test=True).run(source=source)

    actual = captured_stdout.getvalue()[:-1] 
    if actual != expected:
        print(f"{test} failed")
        if verbose:
            print(f"Expected:\n{expected}\n")
            print(f"Actual:\n{actual}\n\n")
        return 0
    else:
        return 1


def run_tests(dir_):
    passes = 0
    for i, test in enumerate(pathlib.Path(dir_).glob('*/*.lox')):
        try:
            passes += run_test(test, verbose=False)
        except Exception:
            print(logging.exception(f"\nSuper failure on {test}"))
        
    print(f"{passes} / {1 + i}")

if __name__ == "__main__":
    run_tests("test")
    
