from collections import namedtuple

Block = namedtuple("Block", ("statements"))
Expression = namedtuple("Expression", ("expression"))
Function = namedtuple("Function", ("name", "params", "body"))
If = namedtuple("If", ("condition", "then_branch", "else_branch"))
Print = namedtuple("Print", ("expression"))
Var = namedtuple("Var", ("name", "initializer"))
While = namedtuple("While", ("condition", "body"))
