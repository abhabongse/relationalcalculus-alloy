"""Helpers for AST node classes constructor."""

import re

############################################################
## String pattern matching to check for valid identifiers ##
############################################################
# Regular expression pattern for identifiers
ALPHAID_RE = re.compile(r'[A-Za-z][A-Za-z0-9_]*')
UPPERID_RE = re.compile(r'[A-Z][A-Za-z0-9_]*')
LOWERID_RE = re.compile(r'[a-z][A-Za-z0-9_]*')

def is_alpha_id(name):
    """Whether ``name`` a valid regular identifier is ASDL."""
    return bool(ALPHAID_RE.fullmatch(name))

def is_upper_id(name):
    """Whether ``name`` a valid lower-leading identifier is ASDL,
    mostly for constructor identifiers.
    """
    return bool(UPPERID_RE.fullmatch(name))

def is_lower_id(name):
    """Whether ``name`` a valid upper-leading identifier is ASDL,
    mostly for type identifiers.
    """
    return bool(LOWERID_RE.fullmatch(name))
