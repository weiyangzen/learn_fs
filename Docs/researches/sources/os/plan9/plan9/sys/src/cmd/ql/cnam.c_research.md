# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/cnam.c

Class-name table for `ql` linker diagnostics/debugging.

Key responsibilities:
- Defines string names for operand classes used by the PowerPC linker optab machinery.
- Covers register, floating register, condition register, special register, segment register, constant ranges, branch ranges, auto/extern/oreg ranges, FPSCR/MSR/XER/LR/CTR, address, any, and fallback classes.

Dependencies:
- Consumed by linker listing/diagnostic code that prints optab classes.

Notable risks:
- The table order must match the operand-class enum in `l.h`.
- This file contains data only; mismatches would produce misleading diagnostics rather than direct code generation changes.
