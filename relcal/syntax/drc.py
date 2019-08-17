"""
Lark parser and AST definition for Domain Relational Calculus.
"""
from relcal.syntax.helpers import get_lark_parser

drc_parser = get_lark_parser("drc.lark")
