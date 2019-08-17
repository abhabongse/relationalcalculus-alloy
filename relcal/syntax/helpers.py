"""
Helper functions for languages.
"""
import os
from typing import Union

from lark import Lark

from relcal.config import DEBUG_MODE

this_dir = os.path.dirname(os.path.abspath(__file__))


def get_lark_parser(fp: Union[str, bytes, os.PathLike]) -> Lark:
    """
    Construct a Lark parser from a given path of file
    relative to the directory containing source file of this function.

    Args:
        fp: Path to Lark EBNF syntax file.

    Returns:
        An instance of Lark parser.
    """
    fp = os.fspath(fp)
    fp = os.path.join(this_dir, fp)
    with open(fp) as fobj:
        return Lark(fobj.read(), debug=DEBUG_MODE)
