# File Research: sources/os/plan9/9front/sys/src/cmd/5c/list.c

This file installs and implements diagnostic/listing formatters for ARM backend objects.

Key routines:
- `listinit()` registers formatters for instructions, opcodes, symbols, names, bitsets, operands, and register lists.
- `Bconv()` prints variable bitsets using the backend `var[]` table.
- `Pconv()` prints a `Prog`, including condition suffixes and special cases for long multiply, `MOVM`, `DATA`, `TEXT`, and optional middle register operands.
- `Aconv()` prints opcode names from `anames[]`.
- `Dconv()` prints `Adr` operands: constants, shifts, offset registers, register pairs, integer/floating registers, PSR, branches, float constants, and string constants.
- `Rconv()` formats `MOVM` register masks as `[R...]`.
- `Sconv()` escapes 8-byte string constants.
- `Nconv()` prints symbol/name addressing forms for extern, static, auto, and parameter operands.

Dependencies and interactions:
- Uses `gc.h`, `anames[]`, `var[]`, `pc`, `zprog`, and ARM operand constants.
- Used by debug flags and diagnostics throughout code generation, register allocation, and peephole optimization.

Research relevance:
- Important support code for understanding and debugging backend output.

Risk notes:
- `Dconv()` branch display uses global `pc`, so context matters.
- `Rconv()` assumes it is passed a constant register mask; default path can return an uninitialized string if misused.
