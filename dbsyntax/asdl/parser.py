"""ASDL Parser implemented in pyparsing.

Simply call the standalone function `parser` with the source code string
in order parse the source code.
"""
from string import (
    ascii_uppercase as uppers, ascii_lowercase as lowers, digits
    )

from pyparsing import (
    Group, Literal, Regex, Suppress, Word, Optional, ZeroOrMore
    )

from . import ast

##############################
## Parsing helper functions ##
##############################

def parser(source_code):
    """Use grammar defined by pyparsing to parse the given source code
    and construct the tree according to pre-defined AST.
    """
    return Program.parseString(source_code, parseAll=True)[0]

def delimitedList(expr, delim=',', combine=False):
    """Grammar constructor for delimited list. This function is similar
    to `pyparsing.delimitedList` but using '-' operator instead of '+'
    to prevent backtracking of grammar parsing so that better error
    messages is shown while parsing.
    """
    name = f'{expr} [{delim} {expr}]...'
    if combine:
        return Combine(expr - ZeroOrMore(delim + expr)).setName(name)
    else:
        return (expr - ZeroOrMore(Suppress(delim) + expr)).setName(name)

############################################
## ASDL tokens (apart from string module) ##
############################################

alphas = uppers + lowers + '_'
alphanums = alphas + digits
typeId = Word(lowers, alphanums).setName('type identifier')
constructorId = Word(uppers, alphanums).setName('constructor identifier')
anyId = (typeId | constructorId).setName('identifier')

# Comments in ASDL starts with double dash '--' until line end
dblDashComment = Regex(r'\-\-(?:\\\n|[^\n])*').setName('comments')

###############################
## ASDL Parse tree structure ##
###############################

def xlist(iterable):
    iterable = list(iterable)
    print(repr(iterable))
    return iterable

Field = (
    typeId
    + Optional(Literal('?') | Literal('*'), default='')
    + Optional(anyId, default=None)
    ).setParseAction(ast.Field.make)

Fields = Group(
    Suppress(Literal('('))
    - delimitedList(Field, delim=',').setParseAction()
    + Suppress(Literal(')'))
    )

Constructor = (
    constructorId.setName('constructor') + Optional(Fields, default=[])
    ).setParseAction(ast.Constructor.make)

SumType = (
    Group(delimitedList(Constructor, delim='|')) +
    Optional(Suppress('attributes') + Fields, default=None)
    ).setParseAction(ast.SumType.make)

ProductType = Fields.copy().setParseAction(ast.ProductType.make)

Type = (SumType | ProductType).setName('sum type or product type')

Definition = (
    typeId - Suppress(Literal('=')) + Type
    ).setParseAction(ast.Definition.make)

Program = Group(
    ZeroOrMore(Definition).ignore(dblDashComment)
    ).setParseAction(ast.Program.make)

#################################
## Main program execution tool ##
#################################

def _get_program_args(args=None):
    """Parse command line program arguments."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('source_file', nargs='?')
    if args is None:
        return parser.parse_args()  # uses sys.args[1:]
    return parser.parse_args(args)

def _get_source_content(source_fname):
    """Obtain entire text from source file."""
    import sys
    if source_fname is None:
        return sys.stdin.read()
    with open(source_fname) as sf:
        return sf.read()

def _main():
    program_args = _get_program_args()
    source_content = _get_source_content(program_args.source_file)
    print(parser(source_content))

if __name__ == '__main__':
    _main()
