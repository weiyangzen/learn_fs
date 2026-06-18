# File Research: sources/os/plan9/9front/sys/src/cmd/7l/list.c

Debug/listing formatter support for ARM64 linker instructions and operands.

Key functions:
- `listinit` installs Plan 9 format verbs for opcodes, operands, programs, strings, names, and classes.
- `Pconv` formats one `Prog`, including special display for `ADATA`, `AINIT`, and `ADYNT`.
- `Aconv` maps opcode numbers to `anames[]`.
- `Dconv` formats `Adr` operands: constants, registers, stack pointer, shifts, extended registers, register-offset addressing, branches, floating constants, string constants, and special registers.
- `Nconv` formats named offsets for extern/static/auto/param operands.
- `Rconv` maps operand class IDs to `cnames[]`.
- `Sconv` escapes fixed-size Plan 9 string constants.
- `prasm` prints one instruction.
- `diag` prints an error prefixed by current function name and aborts after too many errors.

Important details:
- Uses `curp` and `curtext` for context-sensitive branch and diagnostic formatting.
- Knows ARM64 condition-code names and selected special registers (`FPSR`, `FPCR`, `NZCV`).
- Diagnostic reporting is global and increments `nerrors`.

Filesystem relevance: none directly; developer/debug infrastructure for the linker.
