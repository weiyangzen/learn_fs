# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/list.c

Purpose: Formatting and diagnostics for linker programs and operands.

Key behavior:
- `listinit` installs custom formatters for assembler opcodes, addresses, programs, strings, and name-bearing addresses.
- `Pconv` formats a `Prog` instruction, including scheduler marker and optional third register.
- `Aconv` maps opcode numbers to assembler names.
- `Dconv` formats address modes and constants.
- `Nconv` formats symbol-relative names such as SB/SP/FP references.
- `Sconv` escapes fixed-size string constants.
- `diag` prints current text symbol context, increments error count, and exits after too many errors.

Dependencies:
- Uses linker structures/globals from `l.h`, assembler name table, and Plan 9 formatting.

Notable details:
- Diagnostic context defaults to the current function symbol when available.
