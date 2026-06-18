# File Research: sources/os/plan9/9front/sys/src/cmd/qc/list.c

Formatting/debug printing support for the Power compiler backend.

Key responsibilities:
- `listinit` installs custom formatters for opcodes, programs, symbols, operands, nodes, and bitsets.
- `Bconv` prints liveness/variable bitsets using `var[]`.
- `Pconv` formats `Prog` instructions, including `DATA`, `TEXT`, normal two-operand, and `from3` three-operand instructions.
- `Aconv` maps opcode numbers through `anames`.
- `Dconv`, `Sconv`, and `Nconv` format addressing modes, string constants, and symbol-relative names.

Dependencies and coupling:
- Depends on `gc.h`, `anames`, `pc`, and register/address constants.
- Used by debug flags in codegen, register allocation, and peephole optimization.

Notable behavior:
- Handles Power-specific register classes (`R`, `F`, `C`) and Plan 9 symbol names (`SB`, `SP`, `FP` style).
