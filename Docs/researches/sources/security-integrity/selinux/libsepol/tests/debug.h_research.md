# sources/security-integrity/selinux/libsepol/tests/debug.h

## Purpose
`debug.h` declares test debugging helpers for bitmaps and conditional expressions.

## APIs and Integration
It declares `print_ebitmap(ebitmap_t *bitmap, FILE *fp)` and `display_expr(policydb_t *p, cond_expr_t *exp, FILE *fp)`, including policydb and conditional definitions needed by test files.

## Risks and Test Signals
The viewed file lacks an include guard, but duplicate declarations are benign. Build coverage and verbose diagnostics exercise it.
