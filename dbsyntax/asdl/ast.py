"""Minimal Abstract Syntax Tree (AST) for ASDL."""

from collections import namedtuple

######################
## Helper functions ##
######################

def _sanitize_token(token):
    """Convert a given token into nested lists as per pyparsing."""
    if hasattr(token, 'asList'):
        return token.asList()
    return token

#########################
## Simple AST for ASDL ##
#########################
# TODO: AST node type verification (verify parameter values)

class AST(object):
    # Declaring '__slots__' in every class definitions previous
    # setting key-value data in '__dict__' when subclassing tuple.
    __slots__ = ()

    @classmethod
    def make(cls, tokens):
        tokens = [_sanitize_token(token) for token in tokens]
        return cls(*tokens)

class Program(AST, namedtuple('Program', 'definitions')):
    __slots__ = ()

class Definition(AST, namedtuple('Definition', 'type_id type')):
    __slots__ = ()

class AnyType(AST):
    __slots__ = ()

class ProductType(AnyType, namedtuple('ProductType', 'fields')):
    __slots__ = ()

class SumType(AnyType, namedtuple('SumType', 'constructors attributes')):
    __slots__ = ()

class Constructor(AST, namedtuple('Constructor', 'constructor_id fields')):
    __slots__ = ()

class Field(AST, namedtuple('Field', 'type_id modifier attr_name')):
    __slots__ = ()
