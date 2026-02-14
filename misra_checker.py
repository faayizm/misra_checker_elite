
import sys
import os
import argparse
from misra.checker import ASTChecker
from misra.rules import REGEX_RULES
from pycparser import parse_file
import re

# Color codes for Elite Output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_violation(v):
    print(f"{Colors.FAIL}{Colors.BOLD}[Line {v.line}] {v.rule_id}: {v.description}{Colors.ENDC}")
    print(f"   {Colors.WARNING}Match:{Colors.ENDC} {v.match}")
    print(f"   {Colors.OKCYAN}Suggestion:{Colors.ENDC} {v.suggestion}")
    print("-" * 60)

def main():
    parser = argparse.ArgumentParser(description="Elite MISRA C Checker")
    parser.add_argument("file", help="Path to the C file to check")
    parser.add_argument("--json", action="store_true", help="Output in JSON format (not implemented yet)")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"{Colors.FAIL}Error: File {args.file} not found.{Colors.ENDC}")
        sys.exit(1)

    print(f"{Colors.HEADER}Checking {args.file} for MISRA compliance...{Colors.ENDC}\n")
    
    violations = []

    # 1. Regex Checks
    try:
        with open(args.file, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                line_ctx = {'line_content': line, 'line_num': i + 1}
                for rule in REGEX_RULES:
                    v = rule.check(line_ctx)
                    violations.extend(v)
    except Exception as e:
        print(f"Error reading file: {e}")

    # 2. AST Checks
    try:
        # Using fake includes for pycparser
        # We need to make sure the relative path to fake_libc_include is correct
        script_dir = os.path.dirname(os.path.realpath(__file__))
        fake_include = os.path.join(script_dir, 'utils', 'fake_libc_include')
        
        ast = parse_file(args.file, use_cpp=True, cpp_path='clang', cpp_args=['-E', f'-I{fake_include}'])
        
        ast_checker = ASTChecker()
        ast_checker.visit(ast)
        violations.extend(ast_checker.violations)

    except Exception as e:
        print(f"{Colors.WARNING}Warning: AST analysis failed: {e}{Colors.ENDC}")
        print("Running only regex checks.")

    # Sort violations
    violations.sort(key=lambda x: x.line)

    # Report
    if violations:
        for v in violations:
            print_violation(v)
        print(f"\n{Colors.FAIL}Total violations found: {len(violations)}{Colors.ENDC}")
    else:
        print(f"{Colors.OKGREEN}No violations found! Elite code!{Colors.ENDC}")

if __name__ == "__main__":
    main()
