"""Helpers for AST node classes constructor."""

import re

###################################################
## Low-level predicate which checks for validity ##
## of identifiers via strings pattern matching.  ##
###################################################
# Regular expression pattern for identifiers
ALPHAID_RE = re.compile(r'[A-Za-z][A-Za-z0-9_]*')
UPPERID_RE = re.compile(r'[A-Z][A-Za-z0-9_]*')
LOWERID_RE = re.compile(r'[a-z][A-Za-z0-9_]*')

def is_alpha_id(name):
    """Whether ``name`` is a valid alphanumeric identifier in ASDL."""
    return bool(ALPHAID_RE.fullmatch(name))

def is_upper_id(name):
    """Whether ``name`` is a valid lower-leading identifier in ASDL."""
    return bool(UPPERID_RE.fullmatch(name))

def is_lower_id(name):
    """Whether ``name`` a valid upper-leading identifier in ASDL."""
    return bool(LOWERID_RE.fullmatch(name))

##################################################
## Exception raising version of functions which ##
## validate identifiers in the context of ASDL. ##
##################################################

def verify_id(name):
    """Whether ``name`` is a valid alphanumeric identifier in ASDL.
    An exception is raised if identifier is invalid.
    """
    if not isinstance(name, str):
        raise TypeError('must be a string: {name!r}')
    if not is_alpha_id(name):
        raise ValueError(f'must be a valid alphanumeric identifier: {name!r}')

def verify_constructor_id(name):
    """Whether ``name`` a valid alphanumeric, uppercase-leading
    string suitable for constructor identifier in ASDL. An exception
    is raised if identifier is invalid.
    """
    verify_id(name)
    if not is_upper_id(name):
        raise ValueError('must be an uppercase-leading constructor identifier: '
                         f'{name!r}')

def verify_type_id(name):
    """Whether ``name`` a valid alphanumeric, lowercase-leading
    string suitable for type identifier in ASDL. An exception
    is raised if identifier is invalid.
    """
    verify_id(name)
    if not is_lower_id(name):
        raise ValueError('must be a lowercase-leading constructor identifier: '
                         f'{name!r}')
