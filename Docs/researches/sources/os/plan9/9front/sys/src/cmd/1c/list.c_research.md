# File Research: sources/os/plan9/9front/sys/src/cmd/1c/list.c

Debug/listing formatter support for the `1c` backend.

Key responsibilities:
- Installs formatters for registers, opcodes, addresses, instructions, string constants, and bitsets.
- `Bconv` prints compiler variable bitsets using `var[]`.
- `Pconv` prints a `Prog` as mnemonic plus operands, including bitfield widths/shifts.
- `Aconv` maps opcode numbers through `anames`.
- `Dconv` formats `Adr` values including indirect, pre/post increment/decrement, address constants, branches, extern/static/auto/param, constants, floats, and strings.
- `Rconv` formats data/address/FP registers and special 68000 registers.
- `Sconv` escapes fixed-size string constants.

Notable details:
- These formatters are used by debug flags throughout code generation and optimization, so correctness here affects diagnostics and developer visibility.
