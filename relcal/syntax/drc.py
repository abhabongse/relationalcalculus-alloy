"""
Lark parser and AST definition for Domain Relational Calculus.
"""
from typing import Dict, NamedTuple, Tuple

from lark import Lark, Tree, Transformer, v_args

drc_parser = Lark("""
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
          | _FOR_ALL_OP "[" FIELD_NAME "]" "(" or_test ")"  -> for_all
          | _THERE_EXISTS_OP "[" FIELD_NAME "]" "(" or_test ")" -> there_exists
         
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
""", parser="lalr", debug=True)

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


#########################
# Lark tree transformer #
#########################

class DRCTreeTransformer(Transformer):
    """
    Parse tree transformer for DRC syntax grammar.
    """

    @v_args(inline=True)
    def start(self, table_defs, query):
        return DRCExtractedData(table_defs, query)

    def table_defs(self, tables):
        return dict(tables)

    @v_args(inline=True)
    def table(self, table_name, fields):
        return Table(str(table_name), fields)

    def fields(self, field_names):
        field_names = tuple(str(name) for name in field_names)
        found = set()
        for name in field_names:
            if name in found:
                raise ValueError(f"duplicated field name: {name}")
            found.add(name)
        return field_names

    @v_args(inline=True)
    def query(self, tuple_vars, predicate):
        return Query(tuple_vars, predicate)


drc_tree_transformer = DRCTreeTransformer()


##################
# Main functions #
##################

def extract_tree_data(tree: Tree) -> DRCExtractedData:
    """
    Obtain the table definitions from DRC syntax tree
    as a dictionary mapping from table names to tuple of field names.
    """
    return drc_tree_transformer.transform(tree)
