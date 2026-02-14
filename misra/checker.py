
import sys
import re
from pycparser import c_ast
from misra.scope import SymbolTable
from misra.rules import AST_RULES, SEMANTIC_RULES

class ASTChecker(c_ast.NodeVisitor):
    def __init__(self):
        self.violations = []
        self.symbol_table = SymbolTable()
        self.ast_rules = AST_RULES
        self.semantic_rules = SEMANTIC_RULES

    def visit(self, node):
        """Override visit to run AST rules on every node."""
        if node is None: return
        
        # Run generic AST rules (structure based)
        for rule in self.ast_rules:
            # We can optimize by checking node type in rule, but for now simple iteration
            # Ideally rule.check() handles type checking
            try:
                # Some rules might look for specific node types
                v = rule.check({'node': node, 'scope': self.symbol_table})
                if v: self.violations.extend(v)
            except Exception as e:
                # print(f"Error running rule {rule.rule_id}: {e}")
                pass

        super().visit(node)

    def visit_FuncDef(self, node):
        func_name = node.decl.name
        self.symbol_table.define(func_name, 'func', line=node.coord.line)
        self.symbol_table.enter_scope()
        
        # Define parameters
        if node.decl.type.args:
            for param in node.decl.type.args.params:
                self._define_vars(param)

        self.visit(node.body)
        self.symbol_table.exit_scope()

    def visit_Compound(self, node):
        self.symbol_table.enter_scope()
        self.generic_visit(node)
        self.symbol_table.exit_scope()

    def visit_Decl(self, node):
        # Variable declaration
        self._define_vars(node)
        self.generic_visit(node)

    def _define_vars(self, node):
        if hasattr(node, 'name') and node.name:
            # Check shadowing before defining
            # Usually strict MISRA 5.3: Inner scope shall not hide outer scope
            # We run semantic rules here on the 'define' event
            for rule in self.semantic_rules:
                if rule.rule_id == "Rule 5.3":
                     v = rule.check({
                         'event': 'define',
                         'name': node.name,
                         'scope': self.symbol_table,
                         'line': node.coord.line
                     })
                     if v: self.violations.extend(v)

            self.symbol_table.define(node.name, 'var', line=node.coord.line)
