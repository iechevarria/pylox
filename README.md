# pylox

Feature-complete Python interpreter for [Bob Nystrom](http://journal.stuffwithstuff.com/)'s [Lox](https://craftinginterpreters.com/the-lox-language.html) programming language. I made this as I read the first half of [Crafting Interpreters](https://craftinginterpreters.com/), which I'd strongly recommend.

## Overview

pylox is a tree-walk interpreter with a fairly simple structure. First, the **scanner** scans Lox source code and converts it into tokens. The **parser** takes these tokens and creates a syntax tree. Next, the **resolver** does a single pass over the syntax tree and handles getting scopes correct. Finally, using the information from the resolver and the syntax tree from the parser, the **interpreter** actually runs code.

## Contents

The table lays out important directories/files and their purposes:

| directory/file       | description                                                                                                    |
| -------------------- | -------------------------------------------------------------------------------------------------------------- |
| lox/                 | Directory with actual Lox interpreter implementation                                                           |
| lox/environment.py   | Holds a given scope's values for the interpreter                                                               |
| lox/error_handler.py | Logs and keeps track of errors                                                                                 |
| lox/interpreter.py   | Executes statements                                                                                            |
| lox/lox_.py          | Runs Lox code from a file or in a REPL on the command line                                                     |
| lox/parser_.py       | Turns tokens from the scanner into a syntax tree                                                               |
| lox/resolver.py      | Resolves variable scopes using the syntax tree from the parser                                                 |
| lox/scanner.py       | Turns raw Lox source code into tokens                                                                          |
| test/                | Lox tests from the main [Crafting Interpreters Repository](https://github.com/munificent/craftinginterpreters) |
| tool/                | Garbage metaprogramming hacks (don't do this)                                                                  |
| run_tests.py         | Script to run tests                                                                                            |

