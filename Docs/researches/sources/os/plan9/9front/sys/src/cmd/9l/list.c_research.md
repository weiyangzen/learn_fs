# File Research: sources/os/plan9/9front/sys/src/cmd/9l/list.c

This file implements formatting and diagnostics for linker instructions, operands, opcodes, strings, and classes.

Key routines:
- `listinit` installs custom formatters `%A`, `%D`, `%P`, `%S`, `%N`, and `%R`.
- `prasm` prints a single `Prog`.
- `Pconv` formats full instructions, including indexed forms and `NOSCHED` markers.
- `Aconv` converts opcode numbers to assembler names.
- `Dconv` formats raw operand address modes.
- `Nconv` formats symbol-relative operands such as `SB`, `SP`, and `FP`.
- `Rconv` formats operand class names through `cnames`.
- `Sconv` escapes string constants.
- `diag` reports errors scoped to the current text symbol and aborts after too many errors.

Important interactions:
- Used throughout linker diagnostics, debug listings, and illegal-combination reporting.
- Depends on `anames`, `cnames`, `curp`, `curtext`, and `INITTEXT`.

Research notes:
- `Dconv` handles Power64 special registers (`XER`, `LR`, `CTR`), FPSCR/MSR, branches, floating constants, and string constants.
- `diag` increments global `nerrors`, which drives `errorexit` cleanup behavior.
