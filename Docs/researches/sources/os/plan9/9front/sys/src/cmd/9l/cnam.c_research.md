# File Research: sources/os/plan9/9front/sys/src/cmd/9l/cnam.c

This file defines `cnames`, the printable names for linker operand classes.

Key content:
- Maps `C_*` class enum values from `l.h` to strings such as `REG`, `FREG`, `SCON`, `LCON`, `SBRA`, `LAUTO`, `SEXT`, `LR`, `CTR`, `ADDR`, and `NCLASS`.

Important interactions:
- Used by `list.c:Rconv` for diagnostics and assembly listing output.
- Must stay aligned with the operand class enum in `l.h`.

Research notes:
- This is a pure diagnostic/listing support table; it has no code-generation logic.
