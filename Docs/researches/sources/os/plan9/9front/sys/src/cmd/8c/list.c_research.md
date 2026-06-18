# File Research: sources/os/plan9/9front/sys/src/cmd/8c/list.c

This file installs and implements debug/listing format conversions for the 386 compiler backend.

Key responsibilities:
- `listinit()` registers custom formatters for opcodes, programs, symbols/strings, operands, registers, and bitsets.
- `Pconv()` formats `Prog` instructions, including special `DATA` and `TEXT` pseudo-op layout.
- `Aconv()` maps opcode numbers to `anames[]`.
- `Dconv()` formats `Adr` operands, including indirect forms, branches, extern/static/auto/param references, constants, floating constants, string constants, and address constants.
- `Rconv()` maps register operand codes to textual register names.
- `Sconv()` escapes fixed-size string constants for debug printing.
- `Bconv()` formats register optimizer bitsets as variable names or offsets.

Integration points:
- Used by diagnostics and debug flags throughout `8c`.
- Depends on `anames[]`, `var[]`, `pc`, and `zprog` conventions.
- Formatting must track operand encodings from `8.out.h`.

Risks and invariants:
- `Dconv()` temporarily mutates `Adr` fields when formatting `D_ADDR`, then restores them.
- Register-name coverage must remain aligned with `D_*` numeric ranges.
