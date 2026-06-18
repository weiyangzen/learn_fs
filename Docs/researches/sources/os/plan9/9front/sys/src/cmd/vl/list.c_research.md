# File Research: sources/os/plan9/9front/sys/src/cmd/vl/list.c

This file implements diagnostic/listing formatters for linker instructions and operands.

Key behavior:
- `listinit` registers Plan 9 format verbs `%A`, `%D`, `%P`, `%S`, and `%N`.
- `Pconv` formats a `Prog` with line number, scheduling marker, opcode, operands, and optional register.
- `Aconv` maps opcode numbers through `anames`.
- `Dconv` formats registers, memory references, constants, branch targets, FP constants, and string constants.
- `Nconv` formats name spaces such as `SB`, `SP`, `FP`, extern/static/auto/param references.
- `Sconv` escapes string constants for listings.
- `diag` prefixes errors with the current text symbol, counts errors, and aborts after more than ten.

Integration and risks:
- `Dconv` depends on global `curp` for branch target formatting.
- These formatters are used heavily by debug flags and error paths; bad formatter assumptions can obscure linker diagnostics.
