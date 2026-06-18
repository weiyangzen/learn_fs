# File Research: sources/os/plan9/9front/sys/src/cmd/9c/list.c

Instruction, operand, symbol-name, string, and bitset formatting for the PowerPC64 compiler backend.

Key functions:
- `listinit` installs formatters for opcodes, programs, strings, names, operands, and bitsets.
- `Pconv` formats `Prog` instructions, including special `DATA` and `TEXT` size/reg fields and explicit GPR/FPR register fields.
- `Aconv` maps opcode enum values to `anames`.
- `Dconv` formats operands including constants, offset-register operands, GPR/FPR/CREG, branches, floating constants, and string constants.
- `Sconv` escapes 8-byte string constants.
- `Nconv` formats symbolic extern/static/auto/param names and raw offsets.
- Includes its own `Bconv` implementation for optimizer bitsets using 64-bit offsets.

Filesystem relevance: indirect debugging/listing support for compiler-generated code.
