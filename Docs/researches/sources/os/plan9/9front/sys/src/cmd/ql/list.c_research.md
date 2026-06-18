# File Research: sources/os/plan9/9front/sys/src/cmd/ql/list.c

This file implements debug and diagnostic formatting for `ql` linker instructions and operands.

Key responsibilities:
- `listinit()` installs formatters for `%A`, `%D`, `%P`, `%S`, `%N`, and `%R`.
- `Pconv()` prints a `Prog`, including special formatting for data directives, indexed addressing, third operands, and NOSCHED markers.
- `Aconv()` converts opcode numbers to assembler names.
- `Dconv()` prints typed addresses: constants, offsets, branches, registers, SPR/DCR/FPSCR/MSR/SREG, floating constants, and string constants.
- `Nconv()` prints symbol-relative names for extern, static, auto, and param addressing.
- `Sconv()` escapes fixed-size string constants.
- `Rconv()` maps operand classes through `cnames`.
- `diag()` reports current-text-prefixed errors and aborts through `errorexit()` after too many errors.

Usage:
- Used throughout the linker for debugging flags and fatal diagnostics.
- `asm.c`, `asmout.c`, `span.c`, `pass.c`, and `obj.c` rely on `%P`, `%D`, `%A`, and `%R` diagnostics.

Implementation notes:
- `curp` and `curtext` are updated during formatting, which diagnostics depend on.
- Branch display adjusts target PCs relative to text/header layout for readability.
