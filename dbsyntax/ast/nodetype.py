"""AST node classes constructor.

There are two possible approaches:
  1. namedtuple-style class constructor
  2. Metaclass (a class constructor which extends `type`)

This package implements a combination of both approaches.
"""
from itertools import chain
from collections.abc import Sequence, Mapping

from .helpers import is_alpha_id, is_upper_id, is_lower_id

#############################
## Main AST implementation ##
#############################

def make_ast(name, spec, builtins):
    """Converts an input which is a new language specification in ASDL
    style (excluding product type) into a collection of node types
    (i.e. constructors for AST node subclasses).

    Arguments:
        name (str): Name of new language, which will also be the common
            class name from which each node type is inherited
        spec (dict): Entire ASDL specification of a new language:
            <spec> ::= Dict[<type_id: str> → <type>, ...]
            <type> ::= Tuple[<constructors>, <attributes>]
            <constructors> ::= Dict[<constructor_id: str> → <fields>, ...]
            <attributes> ::= <fields>
            <fields> ::= Sequence[
                Tuple[<type_id: str>, <modifier>, <attr_name: str>], ...]
            <modifier> ::= '?' | '*' | ''
        builtins (dict): Built-in types

    Returns:
        Mapping from constructor IDs to newly created constructors.
    """
    _verify_spec(spec, builtins)

    # Create a new namespace and initialize with base node type
    namespace = {}
    _make_base_constructor(name, namespace)

    # Create each constructor in namespace
    for constructors, attrs in spec.values():
        for constructor_id, fields in constructors.items():
            combined_fields = list(fields) + list(attrs)
            _make_constructor(constructor_id, combined_fields, namespace)

    return namespace

############################
## Specification checking ##
############################

def _verify_spec(spec, builtins):
    # Specification must be a dictionary
    if not isinstance(spec, Mapping):
        raise TypeError(f'expected a mapping for spec: {spec!r}')

    # Type IDs should be strings of valid format
    for type_id in chain(spec.keys(), builtins.keys()):
        if not isinstance(type_id, str):
            raise TypeError(f'type identifier must be string: {type_id!r}')
        if not is_lower_id(type_id):
            raise ValueError(f'wrong format for type identifier: {type_id!r}')

    # Type IDs in spec must not overlap with builtin types
    spec_type_ids = set(spec.keys())
    builtin_type_ids = set(builtins.keys())
    type_ids = spec_type_ids | builtin_type_ids
    if spec_type_ids & builtin_type_ids:
        raise ValueError(f'overlapped type IDs between spec and builtins')

    # Build each constructor from spec
    seen_constructor_ids = set()
    for constructors, attrs in spec.values():

        # Constructors must be a dictionary
        if not isinstance(constructors, Mapping):
            raise TypeError('expected a mapping for constructors: '
                            f'{constructors!r}')

        # Attributes must be a sequence
        if not isinstance(attrs, Sequence):
            raise TypeError(f'expected a sequence for attributes: {attrs!r}')

        for constructor_id, fields in constructors.items():
            # Constructor ID should be string of valid format
            if not isinstance(constructor_id, str):
                raise TypeError('constructor identifier must be string: '
                                f'{constructor_id!r}')
            if not is_upper_id(constructor_id):
                raise ValueError('wrong format for constructor identifier: '
                                 f'{constructor_id!r}')

            # Constructor ID must not be a duplicate
            if constructor_id in seen_constructor_ids:
                raise ValueError(f'duplicated constructor: {constructor_id!r}')
            seen_constructor_ids.add(constructor_id)

            # Fields must be a list
            if not isinstance(fields, Sequence):
                raise TypeError(f'expected a sequence for fields: {fields!r}')

            # Combined fields and attributes must not overlap
            combined_fields = list(fields) + list(attrs)
            seen_attr_names = set()
            for type_id, modifier, attr_name in combined_fields:
                if type_id not in type_ids:
                    raise ValueError(f'unknown type identifier: {type_id!r}')
                if modifier not in ('*', '?', ''):
                    raise ValueError(f'invalid modifier: {modifier!r}')
                if not isinstance(attr_name, str):
                    raise TypeError('attribute name must be string: '
                                    f'{attr_name!r}')
                if attr_name and not is_alpha_id(attr_name):
                    raise ValueError('wrong format for attribute name: '
                                     f'{attr_name!r}')
                if attr_name and attr_name in seen_attr_names:
                    raise ValueError('duplicated attribute names: '
                                     f'{attr_name!r}')
                seen_attr_names.add(attr_name)

###############################
## Helper AST implementation ##
###############################

def _make_base_constructor(name, namespace):
    # TODO: implement this
    return
    raise NotImplementedError

def _make_constructor(constructor_id, fields, namespace):
    # TODO: implement this
    namespace[constructor_id] = fields
    return
    raise NotImplementedError

# nodetype.make_ast(
#     'NewLanguage',
#     {'expr': ({'Number': [('int', '', 'num')],
#                'BinaryOp': [('expr', '', 'left'), ('expr', '', 'right')],
#                'UnaryOp': [('expr', '', 'val')]},
#               [('str', '', 'lineno')])},
#     {'int': int, 'str': str},
#     )

# ################################################################################
# ### namedtuple
# ################################################################################
#
# _class_template = """\
# from builtins import property as _property, tuple as _tuple
# from operator import itemgetter as _itemgetter
# from collections import OrderedDict
#
# class {typename}(tuple):
#     '{typename}({arg_list})'
#
#     __slots__ = ()
#
#     _fields = {field_names!r}
#
#     def __new__(_cls, {arg_list}):
#         'Create new instance of {typename}({arg_list})'
#         return _tuple.__new__(_cls, ({arg_list}))
#
#     @classmethod
#     def _make(cls, iterable, new=tuple.__new__, len=len):
#         'Make a new {typename} object from a sequence or iterable'
#         result = new(cls, iterable)
#         if len(result) != {num_fields:d}:
#             raise TypeError('Expected {num_fields:d} arguments, got %d' % len(result))
#         return result
#
#     def _replace(_self, **kwds):
#         'Return a new {typename} object replacing specified fields with new values'
#         result = _self._make(map(kwds.pop, {field_names!r}, _self))
#         if kwds:
#             raise ValueError('Got unexpected field names: %r' % list(kwds))
#         return result
#
#     def __repr__(self):
#         'Return a nicely formatted representation string'
#         return self.__class__.__name__ + '({repr_fmt})' % self
#
#     def _asdict(self):
#         'Return a new OrderedDict which maps field names to their values.'
#         return OrderedDict(zip(self._fields, self))
#
#     def __getnewargs__(self):
#         'Return self as a plain tuple.  Used by copy and pickle.'
#         return tuple(self)
#
# {field_defs}
# """
#
# _repr_template = '{name}=%r'
#
# _field_template = '''\
#     {name} = _property(_itemgetter({index:d}), doc='Alias for field number {index:d}')
# '''
#
# def namedtuple(typename, field_names, *, verbose=False, rename=False, module=None):
#     """Returns a new subclass of tuple with named fields.
#
#     >>> Point = namedtuple('Point', ['x', 'y'])
#     >>> Point.__doc__                   # docstring for the new class
#     'Point(x, y)'
#     >>> p = Point(11, y=22)             # instantiate with positional args or keywords
#     >>> p[0] + p[1]                     # indexable like a plain tuple
#     33
#     >>> x, y = p                        # unpack like a regular tuple
#     >>> x, y
#     (11, 22)
#     >>> p.x + p.y                       # fields also accessible by name
#     33
#     >>> d = p._asdict()                 # convert to a dictionary
#     >>> d['x']
#     11
#     >>> Point(**d)                      # convert from a dictionary
#     Point(x=11, y=22)
#     >>> p._replace(x=100)               # _replace() is like str.replace() but targets named fields
#     Point(x=100, y=22)
#
#     """
#
#     # Validate the field names.  At the user's option, either generate an error
#     # message or automatically replace the field name with a valid name.
#     if isinstance(field_names, str):
#         field_names = field_names.replace(',', ' ').split()
#     field_names = list(map(str, field_names))
#     typename = str(typename)
#     if rename:
#         seen = set()
#         for index, name in enumerate(field_names):
#             if (not name.isidentifier()
#                 or _iskeyword(name)
#                 or name.startswith('_')
#                 or name in seen):
#                 field_names[index] = '_%d' % index
#             seen.add(name)
#     for name in [typename] + field_names:
#         if type(name) is not str:
#             raise TypeError('Type names and field names must be strings')
#         if not name.isidentifier():
#             raise ValueError('Type names and field names must be valid '
#                              'identifiers: %r' % name)
#         if _iskeyword(name):
#             raise ValueError('Type names and field names cannot be a '
#                              'keyword: %r' % name)
#     seen = set()
#     for name in field_names:
#         if name.startswith('_') and not rename:
#             raise ValueError('Field names cannot start with an underscore: '
#                              '%r' % name)
#         if name in seen:
#             raise ValueError('Encountered duplicate field name: %r' % name)
#         seen.add(name)
#
#     # Fill-in the class template
#     class_definition = _class_template.format(
#         typename = typename,
#         field_names = tuple(field_names),
#         num_fields = len(field_names),
#         arg_list = repr(tuple(field_names)).replace("'", "")[1:-1],
#         repr_fmt = ', '.join(_repr_template.format(name=name)
#                              for name in field_names),
#         field_defs = '\n'.join(_field_template.format(index=index, name=name)
#                                for index, name in enumerate(field_names))
#     )
#
#     # Execute the template string in a temporary namespace and support
#     # tracing utilities by setting a value for frame.f_globals['__name__']
#     namespace = dict(__name__='namedtuple_%s' % typename)
#     exec(class_definition, namespace)
#     result = namespace[typename]
#     result._source = class_definition
#     if verbose:
#         print(result._source)
#
#     # For pickling to work, the __module__ variable needs to be set to the frame
#     # where the named tuple is created.  Bypass this step in environments where
#     # sys._getframe is not defined (Jython for example) or sys._getframe is not
#     # defined for arguments greater than 0 (IronPython), or where the user has
#     # specified a particular module.
#     if module is None:
#         try:
#             module = _sys._getframe(1).f_globals.get('__name__', '__main__')
#         except (AttributeError, ValueError):
#             pass
#     if module is not None:
#         result.__module__ = module
#
#     return result
