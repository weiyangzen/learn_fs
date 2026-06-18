# File Research: sources/os/plan9/9front/sys/src/cmd/ql/cnam.c

This file provides the textual names for `ql` operand classes.

Contents:
- Defines `char *cnames[]`, indexed by the `C_*` operand classification enum in `l.h`.
- Names include register classes, constants, branch ranges, auto/external addressing forms, special registers, wildcard classes, and `NCLASS`.

Usage:
- `list.c` uses `cnames` through `%R` formatting in `Rconv()`.
- `span.c` diagnostics use these names when reporting illegal instruction operand combinations.

Implementation notes:
- This is a small debug/diagnostic support table.
- It must remain in enum order with the `C_*` definitions in `l.h`; mismatches would make diagnostics misleading.
