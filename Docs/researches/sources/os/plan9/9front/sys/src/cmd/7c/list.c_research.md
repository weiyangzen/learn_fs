# File Research: sources/os/plan9/9front/sys/src/cmd/7c/list.c

Formatting and listing support for ARM64 backend instructions, operands, bitsets, registers, and short strings.

Key functions:
- `listinit` installs Plan 9 `fmt` converters for opcodes, programs, operands, names, bitsets, strings, and register lists.
- `Pconv` formats a full `Prog`, including opcode, source operand, data/text size fields, register operand, optional `from3`, and destination.
- `Aconv` maps opcode numbers to `anames`.
- `Dconv` formats `Adr` operands across constants, shifted operands, offset/pre/post-indexed memory, extended registers, GPR/FPR/SP/SPR names, branches, floating constants, and short strings.
- `Rconv` formats register-list constants.
- `Sconv` escapes fixed-width short string constants.
- `Nconv` formats symbolic names for extern/static/auto/param references.

Important details:
- Has specific display support for `FPSR`, `FPCR`, and `NZCV`.
- Uses current `pc` for branch offset formatting.
- The `conds` table is present but unused in the active formatting path.

Filesystem relevance: indirect debugging/listing support.
