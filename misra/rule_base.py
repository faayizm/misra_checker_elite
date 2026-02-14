
from abc import ABC, abstractmethod

class MisraRule(ABC):
    def __init__(self, rule_id, description, severity="Required"):
        self.rule_id = rule_id
        self.description = description
        self.severity = severity

    @abstractmethod
    def check(self, context):
        """
        Perform the check.
        context: Object containing needed data (AST node, line string, symbol table, etc.)
        Returns: List of Violation objects or empty list.
        """
        pass

class Violation:
    def __init__(self, rule_id, line, description, match, suggestion):
        self.rule_id = rule_id
        self.line = line
        self.description = description
        self.match = match
        self.suggestion = suggestion
    
    def __repr__(self):
        return f"[{self.rule_id}] Line {self.line}: {self.description}"

