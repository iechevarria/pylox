from collections import namedtuple

Block = namedtuple("Block", ("statements"))
Expression = namedtuple("Expression", ("expression"))
Print = namedtuple("Print", ("expression"))
Var = namedtuple("Var", ("name", "initializer"))
