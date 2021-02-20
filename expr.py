from collections import namedtuple

Binary = namedtuple("Binary", ("left", "operator", "right"))
Grouping = namedtuple("Grouping", ("expression"))
Literal = namedtuple("Literal", ("value"))
Unary = namedtuple("Unary", ("operator", "right"))
