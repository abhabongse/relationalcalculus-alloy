"""
Lark parser and AST definition for Domain Relational Calculus.
"""
from typing import Dict, List, NamedTuple, Tuple, Union

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

    def transform(self, node: Tree) -> DRCParsedObject:
        """
        Transforms the entire parsed tree into the abstract syntax tree.
        The given parsed tree node must be of type 'start'.
        """
        table_defs_node: Tree
        query_node: Tree
        table_defs_node, query_node = node.children
        table_defs = self.transform_table_defs(table_defs_node)
        query = self.transform_query(query_node)
        return DRCParsedObject(table_defs, query)

    def transform_table_defs(self, table_defs_node: Tree) -> Dict[Token, Fields]:
        """
        Transforms the node with type 'table_defs' into
        a dictionary which maps table name string to field names.
        """
        table_defs = {}
        for table_node in table_defs_node.children:
            name, fields = self.transform_single_table_def(table_node)
            # Check that all table names are unique
            if name in table_defs:
                raise SyntaxError(
                    f"duplicated table name {str(name)!r} "
                    f"at line {name.line} column {name.column}",
                )
            table_defs[name] = fields
        return table_defs

    def transform_single_table_def(self, table_def_node: Tree) -> Table:
        """
        Transforms the node with type 'table' into
        a tuple of table name strings and field names.
        """
        table_name: Token
        fields_node: Tree
        table_name, fields_node = table_def_node.children

        # Check that all field names are unique
        collected = set()
        for field_name in fields_node.children:
            if field_name in collected:
                raise SyntaxError(
                    f"duplicated field name {str(field_name)!r} "
                    f"at line {field_name.line} column {field_name.column}",
                )
            collected.add(field_name)

        return Table(table_name, self.visit_fields(fields_node))

    def transform_query(self, node: Tree) -> Query:
        """
        Transforms the node with type 'query' into the Query tuple object.
        """
        tuple_vars_node: Tree
        predicate_node: Tree
        tuple_vars_node, predicate_node = node.children
        for variable in tuple_vars_node.children:
            self.validate_shadowing(variable, predicate_node)
        return Query(self.visit_fields(tuple_vars_node), self.visit(predicate_node))

    def validate_shadowing(self, variable: Token, subtree: Tree):
        """
        Makes sure that the subtree does not introduce a new variable
        whose name matches that of the given variable.
        """
        for node in subtree.iter_subtrees():
            if node.data not in ('for_all', 'there_exists'):
                continue  # skip
            checking_token, _ = node.children
            if checking_token == variable:
                raise SyntaxError(
                    f"variable name {str(checking_token)!r} overshadowed "
                    f"at line {checking_token.line} column {checking_token.column}",
                )

    def visit(self, node: Tree):
        """
        Recursively transforms a given node from the Lark parsed tree.
        Specifically, the method 'visit_nodetype' will be invoked with such node
        where 'nodetype' is the type of the node represented by 'node.data'.
        Otherwise, an AttributeError is raised.
        """
        return object()  # TODO: implement this
        # visitor = getattr(self, f"visit_{node.data}")
        # return visitor(node)

    def visit_fields(self, node: Tree):
        return tuple(node.children)
