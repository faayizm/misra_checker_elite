# Elite MISRA C Checker

A powerful, extensible, and pure-Python static analysis tool for checking MISRA C:2012 guidelines.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

## 🚀 Overview

This tool provides a lightweight yet robust way to check C validation against key MISRA rules without the overhead of heavy commercial tools. It leverages `pycparser` for AST analysis and a semantic symbol table to detect complex violations like variable shadowing and control flow integrity.

### Key Features
- **No External Binary Dependencies**: Runs purely on Python (requires `clang` only for preprocessing, which is optional if you provide preprocessed files).
- **Semantical Analysis**: Tracks variable scope, shadowing, and type usage.
- **Hybrid Engine**: Combines AST traversal for structural rules and Regex for lexical/naming rules.
- **Elite Reporting**: Colorized, structured output with actionable code suggestions.
- **Extensible**: Modular architecture allows adding new rules in minutes.

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/faayizm/misra_checker_elite.git
   cd misra_checker_elite
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: This project relies on `pycparser`.*

3. **Prerequisites**
   - Python 3.8+
   - `clang` (or any C preprocessor) in your system PATH (used for handling macros/includes).

## 🏃 Usage

Run the checker on any C file:

```bash
python3 misra_checker.py path/to/your/file.c
```

### Example
Try running it on the provided sample:
```bash
python3 misra_checker.py samples/test.c
```

**Output:**
```
[Line 14] Rule 5.3: An identifier declared in an inner scope shall not hide an identifier in an outer scope.
   Match: Variable 'x'
   Suggestion: Rename variable. Shadows declaration at line 10.
```

## 🏗️ Developer Guide

We designed this project to be easily extensible. Here is how you can add your own rules.

### Project Structure
- `misra_checker.py`: Entry point.
- `misra/checker.py`: Main AST Visitor and logic coordinator.
- `misra/rule_base.py`: Base class for all rules.
- `misra/rules.py`: Collection of implemented rules.
- `misra/scope.py`: Symbol table implementation.

### Adding a New Rule

1.  Open `misra/rules.py`.
2.  Define a new class inheriting from `MisraRule`.
3.  Implement the `check(self, context)` method.

**Example: Adding a rule to ban `while(1)`**

```python
class NoInfiniteWhile(MisraRule):
    def __init__(self):
        super().__init__("Rule 12.3", "Infinite while loops are not allowed.")

    def check(self, context):
        node = context.get('node')
        # Check if node is While and condition evaluates to constant 1 (simplified)
        if isinstance(node, c_ast.While):
            # ... logic to check condition ...
            return [Violation(self.rule_id, node.coord.line, self.description, "while(1)", "Use for(;;) or limit loop.")]
        return []
```

4.  Add your rule instance to the `AST_RULES` list at the bottom of `misra/rules.py`.

## 📜 Supported Rules (Subset)
| Rule | Description |
|------|-------------|
| **Dir 4.6** | Use fixed-width integers (int32_t) instead of basic types. |
| **Rule 5.1** | External identifiers must be unique and <31 chars. |
| **Rule 5.3** | No shadowing of identifiers in outer scopes. |
| **Rule 15.1** | Do not use `goto`. |
| **Rule 15.6** | Control flow bodies must be compound `{}`. |
| **Rule 16.4** | Switch statements must have a `default` case. |

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a Pull Request.

## 📄 License
MIT License
