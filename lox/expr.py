from collections import namedtuple

Array = namedtuple("Array", ("values"))
Assign = namedtuple("Assign", ("name", "value"))
Binary = namedtuple("Binary", ("left", "operator", "right"))
Call = namedtuple("Call", ("callee", "paren", "expressions"))
Get = namedtuple("Get", ("object", "name"))
Grouping = namedtuple("Grouping", ("expression"))
Literal = namedtuple("Literal", ("value"))
Logical = namedtuple("Logical", ("left", "operator", "right"))
Set = namedtuple("Set", ("object", "name", "value"))
Unary = namedtuple("Unary", ("operator", "right"))
Variable = namedtuple("Variable", ("name"))
