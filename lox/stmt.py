from collections import namedtuple

Block = namedtuple("Block", ("statements"))
Class = namedtuple("Class", ("name", "methods"))
Expression = namedtuple("Expression", ("expression"))
Function = namedtuple("Function", ("name", "params", "body"))
If = namedtuple("If", ("condition", "then_branch", "else_branch"))
Print = namedtuple("Print", ("expression"))
Return = namedtuple("Return", ("keyword", "value"))
Var = namedtuple("Var", ("name", "initializer"))
While = namedtuple("While", ("condition", "body"))
