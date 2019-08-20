"""
Lark parser and AST definition for Domain Relational Calculus.
"""
import pprint
from typing import Dict, List, NamedTuple, Tuple, Union

from lark import Lark, Token, Tree, Transformer, Visitor, v_args

drc_parser = Lark('''
start: table_defs query
table_defs: (table ";")*
table: TABLE_NAME "(" fields? ")"
fields: FIELD_NAME ("," FIELD_NAME)* ","?
query: "{" fields ":" iff_test "}"

?iff_test: implies_test (_IFF_OP implies_test)?
?implies_test: or_test (_IMPLIES_OP or_test)?
?or_test: and_test (_OR_OP and_test)*
?and_test: not_test (_AND_OP not_test)*
?not_test: _NOT_OP atom_test  -> not
         | atom_test
?atom_test: "(" iff_test ")"
          | table 
          | FIELD_NAME COMP_OP FIELD_NAME  -> compare_op
          | _FOR_ALL_OP "[" FIELD_NAME "]" "(" iff_test ")"  -> for_all
          | _THERE_EXISTS_OP "[" FIELD_NAME "]" "(" iff_test ")" -> there_exists
         
TABLE_NAME: /[A-Z][A-Za-z0-9_]*/
FIELD_NAME: /[a-z][A-Za-z0-9_]*/
QUERY_IDENTIFIER: /\$[A-Za-z0-9_]+/

_IFF_OP.10: "<=>" | "⇔" | "↔" | "IFF"
_IMPLIES_OP.10: "=>" | "⇒" | "→" | "IMPLIES"
_OR_OP.10: "∨" | "|" | "OR"
_AND_OP.10: "∧" | "&" | "AND"
_NOT_OP.10: "~" | "¬" | "NOT"
_FOR_ALL_OP.10: "∀" | "ALL"
_THERE_EXISTS_OP.10: "∃" | "EXISTS"

COMP_OP: "==" | "!=" | ">=" | ">" | "<=" | "<"

%import common.WS
%ignore WS
''', parser="lalr", debug=True)

####################
# Type definitions #
####################

Fields = Tuple[str, ...]


class Table(NamedTuple):
    name: str
    fields: Fields


class Query(NamedTuple):
    tuple_vars: Fields
    predicate: Tree


class DRCExtractedData(NamedTuple):
    table_defs: Dict[str, Fields]
    query: Query


class Operation(NamedTuple):
    op_name: str
    args: Tuple[Union['Operation', str], ...]


#######################################
# Lark tree visitors and transformers #
#######################################

# TODO: Lark tree visitors and transformers are not flexible enough
#       Just transform them from scratch.

class ValidateShadowingVisitor(Visitor):
    """
    Parsed tree visitor to validate that no variable shadowing exists.
    """

    @staticmethod
    def validate(variable: Token, tree: Tree):
        for node in tree.iter_subtrees():
            if node.data not in ('for_all', 'there_exists'):
                continue
            token = node.children[0]
            if token == variable:
                raise SyntaxError(f"variable {str(token)!r} overshadowed "
                                  f"at line {token.line} column {token.column}")

    def query(self, tree: Tree):
        fields: Tree
        predicate: Tree
        fields, predicate = tree.children
        for variable in fields.children:
            self.validate(variable, predicate)

    def for_all(self, tree: Tree) -> Tree:
        bound_variable: Token
        predicate: Tree
        bound_variable, predicate = tree.children
        self.validate(bound_variable, predicate)

    def there_exists(self, tree: Tree) -> Tree:
        bound_variable: Token
        predicate: Tree
        bound_variable, predicate = tree.children
        self.validate(bound_variable, predicate)


class DRCExtractionTransformer(Transformer):
    """
    Parsed tree transformer to obtain all table definitions
    from the source data in DRC syntax grammar.
    """

    @v_args(inline=True)
    def start(self, table_defs: Dict[str, Fields], query: Query) -> DRCExtractedData:
        return DRCExtractedData(table_defs, query)

    def table_defs(self, tables: List[Table]) -> Dict[str, Fields]:
        return dict(tables)

    @v_args(inline=True)
    def table(self, table_name: Token, fields: Fields) -> Table:
        return Table(str(table_name), fields)

    def fields(self, field_names: List[Token]) -> Fields:
        return tuple(str(name) for name in field_names)

    @v_args(inline=True)
    def query(self, tuple_vars: Fields, predicate: Tree) -> Query:
        return Query(tuple_vars, predicate)


validate_shadowing_visitor = ValidateShadowingVisitor()
drc_extraction_transformer = DRCExtractionTransformer()


##################
# Main functions #
##################

def extract_tree_data(tree: Tree):
    """
    Obtain the table definitions from DRC syntax tree
    as a dictionary mapping from table names to tuple of field names.
    """
    validate_shadowing_visitor.visit(tree)

    table_defs: Dict[str, Fields]
    query: Query
    table_defs, query = drc_extraction_transformer.transform(tree)

    pprint.pprint(table_defs)
    pprint.pprint(query.tuple_vars)
    print(query.predicate.pretty())
