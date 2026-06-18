# File Research: sources/os/plan9/9front/sys/src/cmd/2c/list.c

Purpose: debug/listing formatters for the 68020 compiler backend.

Key behavior:
- `listinit()` installs custom `Fmt` converters for registers, opcodes, addresses, programs, strings, bitsets, and indexed operands.
- `Bconv()` prints optimizer variable bitsets by resolving bit numbers through `var[]`.
- `Pconv()` prints a `Prog` as opcode plus formatted source/destination operands, including bit-field widths.
- `Aconv()` resolves opcode names through `anames`.
- `Dconv()` renders all compiler/linker addressing forms, including 68020 indexed modes, pre/post increment, indirection, symbol classes, constants, stack, floating constants, and string constants.
- `Rconv()` maps numeric register/special-register IDs to human-readable names.
- `Sconv()` escapes fixed 8-byte string constants.

Research notes:
- This file is non-emitting diagnostic infrastructure, but it is heavily used by debug flags and optimizer warnings.
- `Dconv()` temporarily mutates `Adr` fields while recursively formatting, then restores them.
