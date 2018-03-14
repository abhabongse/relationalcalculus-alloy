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

def _recr_build_repr(param, _indent_accm=0, _indent_size=2):
    """Extracted logic from `AST._build_repr` to deal with primitive
    param data in addition to possibly being AST nodes.
    """
    if param is None:
        return f'{_sp(_indent_accm)}None'
    if isinstance(param, str):
        return f'{_sp(_indent_accm)}{param!r}'
    if isinstance(param, list):
        if not param:
            return f'{_sp(_indent_accm)}[]'
        pprint_params = ',\n'.join(
            _recr_build_repr(p, _indent_accm, _indent_size)
            for p in param
            ).lstrip()
        return f'{_sp(_indent_accm)}[{_sp(_indent_size-1)}{pprint_params}]'
    return param._build_repr(_indent_accm+_indent_size, _indent_size)

def _sp(width):
    return ' ' * width

#########################
## Simple AST for ASDL ##
#########################
# TODO: AST node type verification (verify parameter values)
# TODO: implemented specialized 'namedtuple' just to create a
#       new type of AST nodes

class AST(object):
    """AST nodes."""

    # Declaring '__slots__' in every class definitions previous
    # setting key-value data in '__dict__' when subclassing tuple.
    __slots__ = ()

    @classmethod
    def make(cls, tokens):
        tokens = [_sanitize_token(token) for token in tokens]
        return cls(*tokens)

    def __repr__(self):
        return self._build_repr()

    def _build_repr(self, _indent_accm=0, _indent_size=2):
        """Pretty print of AST nodes."""
        clsname = self.__class__.__name__
        pprint_params = '\n'.join(
            _recr_build_repr(p, _indent_accm+_indent_size, _indent_size)
            for p in self  # 'self' is a tuple itself
            )
        return f'{_sp(_indent_accm)}{clsname}(\n{pprint_params})'

class Program(AST, namedtuple('Program', 'definitions')):
    __slots__ = ()

class Definition(AST, namedtuple('Definition', 'type_id type')):
    __slots__ = ()

class ProductType(AST, namedtuple('ProductType', 'fields')):
    __slots__ = ()

class SumType(AST, namedtuple('SumType', 'constructors attributes')):
    __slots__ = ()

class Constructor(AST, namedtuple('Constructor', 'constructor_id fields')):
    __slots__ = ()

class Field(AST, namedtuple('Field', 'type_id modifier attr_name')):
    __slots__ = ()

    def _build_repr(self, _indent_accm=0, _indent_size=2):
        type_id = repr(self.type_id)
        modifier = repr(self.modifier)
        attr_name = repr(self.attr_name)
        return f'{_sp(_indent_accm)}Field({type_id}, {modifier}, {attr_name})'
