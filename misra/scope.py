
class SymbolTable:
    def __init__(self):
        # Stack of scopes. Each scope is a dictionary of name -> metadata
        self.scopes = [{}] 

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def define(self, name, kind, type_info=None, line=0):
        """
        Define a symbol in the current scope.
        Returns False if already defined in CURRENT scope (redefinition),
        True otherwise.
        """
        current_scope = self.scopes[-1]
        if name in current_scope:
            return False
        current_scope[name] = {
            "kind": kind, # 'var', 'func', 'type'
            "type": type_info,
            "line": line,
            "used": False
        }
        return True

    def lookup(self, name, current_scope_only=False):
        """
        Look up a symbol.
        If current_scope_only is True, check only the top scope.
        Otherwise check all scopes from top to bottom.
        Returns the symbol dict or None.
        """
        if current_scope_only:
            return self.scopes[-1].get(name)
        
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def check_shadowing(self, name):
        """
        Check if 'name' shadows a symbol in outer scopes.
        Returns the shadowed symbol dict or None.
        """
        # Start checking from the second to last scope (parent of current)
        for scope in reversed(self.scopes[:-1]):
            if name in scope:
                return scope[name]
        return None
