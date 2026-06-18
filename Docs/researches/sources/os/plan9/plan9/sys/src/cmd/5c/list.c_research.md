# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/list.c

Formatting and listing helpers for ARM backend instructions and operands.

Key behavior:
- Installs custom formatters for opcodes, programs, string constants, names, bitsets, operands, and register lists.
- `Pconv` formats full `Prog` instructions with condition/suffix decorations.
- `Dconv` formats ARM operand addressing modes, constants, shifts, registers, PSR, branches, FP/string constants.
- `Nconv` formats named operands by storage class: extern, static, auto, param.
- `Rconv` formats MOVM register-list masks.
- `Bconv` formats optimizer bitsets as variable names or offsets.

Notes:
- Used for compiler debugging, listings, and diagnostics rather than final code emission.
