"""
Lark parser and AST definition for Domain Relational Calculus.
"""
from typing import Dict, NamedTuple, Set, Tuple

from lark import Lark, Token, Tree

from relcal import config
from relcal.helpers.primitives import Singleton

####################
# Type definitions #
####################

Fields = Tuple[Token, ...]


class Table(NamedTuple):
    name: Token
    fields: Fields


class Query(NamedTuple):
    tuple_vars: Fields
    predicate: object


class DRCParsedObject(NamedTuple):
    table_defs: Dict[Token, Fields]
    query: Query


########################
# Language definitions #
########################

class DRCQueryLanguage(metaclass=Singleton):
    """
    A collection of methods for domain relational calculus query language.
    The actual Lark parser is stored within 'parser' class attribute.
    """
    parser = Lark(r'''
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
    ''', parser="lalr", debug=config.DEBUG_MODE)

    def parse(self, text: str) -> Tree:
        """
        Use the parser to parse the given domain relational calculus query
        into parsed tree.
        """
        return self.parser.parse(text)

    def transform(self, node: Tree) -> DRCParsedObject:
        """
        Transforms the entire parsed tree into the abstract syntax tree.
        The given parsed tree node must be of type 'start'.
        """
        assert node.data == 'start' and len(node.children) == 2

        table_defs_node: Tree = node.children[0]
        query_node: Tree = node.children[1]

        table_defs = self.transform_table_defs(table_defs_node)
        query = self.transform_query(query_node)

        return DRCParsedObject(table_defs, query)

    def transform_table_defs(self, node: Tree) -> Dict[Token, Fields]:
        """
        Transforms the node with type 'table_defs' into
        a dictionary which maps table name string to field names.
        """
        assert node.data == 'table_defs'

        table_defs = {}
        for table_node in node.children:
            name, fields = self.transform_single_table_def(table_node)
            # Check that all table names are unique
            if name in table_defs:
                raise SyntaxError(
                    f"duplicated table name {str(name)!r} "
                    f"at line {name.line} column {name.column}",
                )
            table_defs[name] = fields
        return table_defs

    def transform_single_table_def(self, node: Tree) -> Table:
        """
        Transforms the node with type 'table' into
        a tuple of table name strings and field names.
        """
        assert node.data == 'table' and len(node.children) == 2

        table_name: Token = node.children[0]
        fields_node: Tree = node.children[1]

        # Check that all field names are unique
        collected = set()
        for field_name in fields_node.children:
            if field_name in collected:
                raise SyntaxError(
                    f"duplicated field name {str(field_name)!r} "
                    f"at line {field_name.line} column {field_name.column}",
                )
            collected.add(field_name)

        return Table(table_name, tuple(fields_node.children))

    def transform_query(self, node: Tree) -> Query:
        """
        Transforms the node with type 'query' into the Query tuple object.
        """
        assert node.data == 'query' and len(node.children) == 2

        tuple_vars_node: Tree = node.children[0]
        predicate_node: Tree = node.children[1]

        tuple_vars = tuple(tuple_vars_node.children)
        self.validate_scope(predicate_node, set(tuple_vars))

        return Query(tuple(tuple_vars_node.children), predicate_node)

    def validate_scope(self, node: Tree, scope: Set[str]):
        """
        Recursively checks that
        1.  There is not variable shadowing of variables from within
            the given scope under the tree node.
        2.  There is no free variable not in scope.
        """
        visitor = getattr(self, f"validate_scope_{node.data}", None)
        if visitor:
            return visitor(node, scope)
        for child_node in node.children:
            if isinstance(child_node, Tree):
                self.validate_scope(child_node, scope)
            elif isinstance(child_node, Token) and child_node.type == 'FIELD_NAME':
                self.validate_free_variable(child_node, scope)

    def validate_scope_there_exists(self, node: Tree, scope: Set[str]):
        assert node.data == 'there_exists'
        return self.validate_scope_quantifier(node, scope)

    def validate_scope_for_all(self, node: Tree, scope: Set[str]):
        assert node.data == 'for_all'
        return self.validate_scope_quantifier(node, scope)

    def validate_scope_quantifier(self, node: Tree, scope: Set[str]):
        assert len(node.children) == 2

        variable: Token = node.children[0]
        expr_node: Tree = node.children[1]

        # Check that new variable is not overshadowed
        if variable in scope:
            raise SyntaxError(
                f"variable name {str(variable)!r} overshadowed "
                f"at line {variable.line} column {variable.column}",
            )
        # Recursively check sub-expression node
        self.validate_scope(expr_node, scope | {variable})

    def validate_free_variable(self, variable: Token, scope: Set[str]):
        if variable not in scope:
            raise SyntaxError(
                f"variable name {str(variable)!r} is a free variable "
                f"at line {variable.line} column {variable.column}",
            )
