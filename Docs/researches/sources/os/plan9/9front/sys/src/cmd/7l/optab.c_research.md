# File Research: sources/os/plan9/9front/sys/src/cmd/7l/optab.c

Instruction selection table for the ARM64 linker encoder.

This file defines `Optab optab[]`, mapping assembly opcodes and operand classes to encoder case numbers, emitted sizes, parameters, and literal/relocation flags.

Covered instruction families:
- `ATEXT` pseudo-instructions.
- Arithmetic and logical instructions with register, shifted-register, extended-register, add-immediate, bitmask-immediate, and large-constant forms.
- Moves, including constant materialization through `MOVK`/`MOVN`/`MOVZ`-style cases.
- Branches, calls, returns, ADR/ADRP, conditional branches, compare/test-and-branch.
- Bitfield/extract/sign-extension/count instructions.
- System instructions, barriers, hints, `ERET`.
- Loads/stores for byte/halfword/word/doubleword, signed/unsigned forms, stack/extern/register offsets, scaled/unscaled offsets, pre/post-indexed modes, register-offset modes, and register pairs.
- Floating-point moves, arithmetic, conversions, compares, conditional compares/selects.
- Atomic load/store exclusive/acquire/release forms.
- Vector/crypto-like entries such as AES/SHA forms.
- Data pseudo-ops `AWORD`, `ADWORD`, `ACASE`, `ABCASE`.

Important fields:
- `a1`, `a2`, `a3` are operand classes matched against `from`, `reg/from3`, and `to`.
- `type` is the encoder case consumed by `asmout`.
- `size` is the instruction expansion size in bytes.
- `param` supplies registers such as `REGSB`/`REGSP` or other encoder parameters.
- Flags such as `LFROM`, `LTO`, and `LPOOL` mark literal/large-constant handling needs.

Filesystem relevance: indirect toolchain backend table.
