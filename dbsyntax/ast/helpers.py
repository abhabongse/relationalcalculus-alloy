"""Helpers for AST node classes constructor."""

import re

############################################################
## String pattern matching to check for valid identifiers ##
############################################################
# Regular expression pattern for identifiers
alphaid_re = re.compile(r'[A-Za-z][A-Za-z0-9_]')
upperid_re = re.compile(r'[A-Z][A-Za-z0-9_]')
lowerid_re = re.compile(r'[a-z][A-Za-z0-9_]')

def isalphaidentifier(name):
    """Whether ``name`` a valid regular identifier is ASDL."""
    return bool(alphaid_re.fullmatch(name))

def isupperidentifier(name):
    """Whether ``name`` a valid lower-leading identifier is ASDL,
    mostly for constructor identifiers.
    """
    return bool(alphaid_re.fullmatch(name))

def isloweridentifier(name):
    """Whether ``name`` a valid upper-leading identifier is ASDL,
    mostly for type identifiers.
    """
    return bool(alphaid_re.fullmatch(name))
