# sources/security-integrity/selinux/libsepol/tests/debug.c

## Purpose
`debug.c` provides lightweight debugging helpers for libsepol tests.

## APIs and Integration
`print_ebitmap()` prints every bit up to `bitmap->highbit`. `display_expr()` prints conditional expression nodes using boolean names from the policydb and operator tokens for NOT/OR/AND/XOR/EQ/NEQ. Test suites can use these helpers while diagnosing bitmap or conditional expression failures.

## Risks and Test Signals
The functions are diagnostic only and do not validate indexes. `display_expr()` assumes valid one-based boolean values. Compile coverage verifies prototype consistency, while verbose test output exercises behavior manually.
