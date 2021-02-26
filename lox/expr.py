from collections import namedtuple

Assign = namedtuple("Assign", ("name", "value"))
Binary = namedtuple("Binary", ("left", "operator", "right"))
Call = namedtuple("Call", ("callee", "paren", "expressions"))
Grouping = namedtuple("Grouping", ("expression"))
Literal = namedtuple("Literal", ("value"))
Logical = namedtuple("Logical", ("left", "operator", "right"))
Unary = namedtuple("Unary", ("operator", "right"))
Variable = namedtuple("Variable", ("name"))
