# File Research: sources/os/plan9/9front/sys/src/cmd/2l/list.c

Purpose: linker debug/listing formatters and diagnostics for `2l`.

Key behavior:
- `listinit()` installs custom `Fmt` converters for registers, opcodes, addresses, strings, and programs.
- `Pconv()` prints line number, opcode, operands, and bit-field metadata for a linker `Prog`.
- `Dconv()` renders linker operands, including branch targets through `pcond`, symbol-relative operands, stack/param forms, constants, quick constants, strings, FPU constants, and indexed/pre/post modes.
- `Rconv()` maps numeric data/address/FPU/special registers to names.
- `Sconv()` escapes 8-byte string constants with linker-specific printable escaping.
- `diag()` prefixes diagnostics with current function/text symbol, increments error count, and exits after too many errors.

Research notes:
- `bigP` is a temporary global used by address formatting so branch operands can print resolved target PCs.
- Formatting code mirrors `2c/list.c` but uses linker `Adr` and final branch-target information.
