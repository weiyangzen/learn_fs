# File Research: sources/os/plan9/9front/sys/src/cmd/vc/list.c

Purpose: Formatting support for debugging/listing MIPS backend instructions, operands, bitsets, and symbols.

Key behavior:
- `listinit` installs custom formatters for opcodes, programs, strings, names, bitsets, and addresses.
- `Bconv` prints variable bitsets as variable names or constants.
- `Pconv` prints `Prog` instructions, with special formats for `ADATA` and `ATEXT`.
- `Aconv` maps opcode numbers through `anames`.
- `Dconv` renders address forms such as constants, memory references, registers, branch targets, string constants, and floating constants.
- `Sconv` quotes fixed-width symbol/string bytes.
- `Nconv` prints symbol addressing relative to `SB`, `SP`, or `FP`.

Dependencies:
- Uses backend globals from `gc.h`, `var[]`, `pc`, and Plan 9 `Fmt`.

Notable details:
- This file defines `EXTERN` before including `gc.h`, making it the owner of many global definitions.
