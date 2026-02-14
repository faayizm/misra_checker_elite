#include <stdint.h>
#include <stdio.h>

// Violation: Dir 4.6 (Use of basic types)
int my_global_int = 10;

// Violation: Rule 5.1 (Identifier length > 31 chars)
int this_is_a_very_long_variable_name_that_exceeds_limits_of_misra_c_2012 = 0;

int x = 5; // Global x

void func() {
  // Violation: Rule 5.3 (Shadowing global x)
  int x = 10;

  // Violation: Rule 15.6 (Body not compound)
  if (x > 5)
    x = 2; // missing {}

  // Violation: Rule 15.1 (goto statement)
  goto label;

label:
  x = x + 1;

  // Violation: Rule 16.4 (Switch without default)
  switch (x) {
  case 1:
    x = 2;
    break;
  }
}

int main() {
  func();
  // Violation: Legacy C++ style comments
  return 0;
}
