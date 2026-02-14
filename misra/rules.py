
import re
from pycparser import c_ast
from misra.rule_base import MisraRule, Violation

# === Regex Rules ===

class Dir4_6(MisraRule):
    def __init__(self):
        super().__init__("Dir 4.6", "Use of basic types (int, char, short, long, float, double) is not allowed. Use stdint types (int32_t, etc.)")
        self.pattern = r"\b(int|short|long|float|double)\b"
    
    def check(self, context):
        # Context is a line string
        violations = []
        line = context.get('line_content')
        line_num = context.get('line_num')
        if not line: return []

        matches = re.finditer(self.pattern, line)
        for match in matches:
            # Simple heuristic to avoid matching inside words or comments (if not stripped)
            # Better: check if it's not part of a larger word
            violations.append(Violation(
                self.rule_id, line_num, self.description, match.group(), 
                "Replace with fixed-width types like int32_t, uint16_t, etc."
            ))
        return violations

class Rule5_1(MisraRule):
    def __init__(self):
        super().__init__("Rule 5.1", "External identifiers shall be distinct. (Checking for length > 31 characters)")
        self.pattern = r"\b[a-zA-Z_][a-zA-Z0-9_]{31,}\b"

    def check(self, context):
        violations = []
        line = context.get('line_content')
        line_num = context.get('line_num')
        if not line: return []

        matches = re.finditer(self.pattern, line)
        for match in matches:
            violations.append(Violation(
                self.rule_id, line_num, self.description, match.group(),
                "Shorten identifier to 31 chars."
            ))
        return violations

class ReviewCppComments(MisraRule):
    def __init__(self):
        super().__init__("Review", "C++ style comments (//) should not be used in purely C90 code.")
        self.pattern = r"//.*"

    def check(self, context):
        violations = []
        line = context.get('line_content')
        line_num = context.get('line_num')
        if not line: return []
        
        if re.search(self.pattern, line):
             violations.append(Violation(
                self.rule_id, line_num, self.description, "// ...",
                "Replace // with /* ... */."
            ))
        return violations

# === AST Rules ===

class Rule15_1(MisraRule):
    def __init__(self):
        super().__init__("Rule 15.1", "The goto statement shall not be used.")

    def check(self, context):
        node = context.get('node')
        if isinstance(node, c_ast.Goto):
             return [Violation(
                self.rule_id, node.coord.line, self.description, f"goto {node.name}",
                "Replace goto with structured control flow."
            )]
        return []

class Rule16_4(MisraRule):
    def __init__(self):
        super().__init__("Rule 16.4", "Switch statement must have a default label.")

    def check(self, context):
        node = context.get('node')
        if isinstance(node, c_ast.Switch):
            if not self._has_default(node.stmt):
                return [Violation(
                    self.rule_id, node.coord.line, self.description, "switch",
                    "Add a 'default: break;' case."
                )]
        return []

    def _has_default(self, node):
        if isinstance(node, c_ast.Default):
            return True
        if isinstance(node, c_ast.Compound):
            for child in node.block_items or []:
                if self._has_default(child): return True
        return False

class Rule16_1(MisraRule):
    def __init__(self):
         super().__init__("Rule 16.1", "Switch case/default labels shall be well-formed.")
    
    def check(self, context):
        # A bit complex to check "well-formedness" fully without deep flow, 
        # but we can check if a switch body is a Compound statement (MISRA requirement)
        node = context.get('node')
        if isinstance(node, c_ast.Switch):
             if not isinstance(node.stmt, c_ast.Compound):
                 return [Violation(
                     self.rule_id, node.coord.line, self.description, "switch body",
                     "Switch body must be a compound statement {}."
                 )]
        return []

class Rule15_6(MisraRule): 
     def __init__(self):
        super().__init__("Rule 15.6", "Body of iteration/selection stmt must be a compound statement.")
    
     def check(self, context):
        node = context.get('node')
        violations = []
        
        # Check If, While, DoWhile, For
        if isinstance(node, (c_ast.If, c_ast.While, c_ast.DoWhile, c_ast.For)):
            # For 'If', check 'iftrue' and 'iffalse'
            if isinstance(node, c_ast.If):
                if node.iftrue and not isinstance(node.iftrue, c_ast.Compound):
                    violations.append(Violation(self.rule_id, node.coord.line, self.description, "if body", "Wrap body in {}."))
                if node.iffalse and not isinstance(node.iffalse, c_ast.Compound):
                    violations.append(Violation(self.rule_id, node.coord.line, self.description, "else body", "Wrap body in {}."))
            # For loops, check 'stmt'
            elif hasattr(node, 'stmt') and not isinstance(node.stmt, c_ast.Compound):
                 violations.append(Violation(self.rule_id, node.coord.line, self.description, "loop body", "Wrap body in {}."))
        
        return violations

class Rule5_3(MisraRule): 
    def __init__(self):
        super().__init__("Rule 5.3", "An identifier declared in an inner scope shall not hide an identifier in an outer scope.")

    def check(self, context):
        # This rule is special, usually handled during AST traversal by the visitor maintaining the symbol table
        # We can implement it here if we pass the symbol table and current definition
        
        # In this architecture, it's better if the Visitor calls this rule when it defines a variable.
        # context: {'event': 'define', 'name': name, 'scope': symbol_table}
        
        event = context.get('event')
        if event == 'define':
            name = context.get('name')
            scope = context.get('scope')
            line = context.get('line')
            
            shadowed = scope.check_shadowing(name)
            if shadowed:
                 return [Violation(
                    self.rule_id, line, self.description, f"Variable '{name}'",
                    f"Rename variable. Shadows declaration at line {shadowed['line']}."
                )]
        return []

# Rule Registry
REGEX_RULES = [Dir4_6(), Rule5_1(), ReviewCppComments()]
AST_RULES = [Rule15_1(), Rule16_4(), Rule16_1(), Rule15_6()]
SEMANTIC_RULES = [Rule5_3()] 

