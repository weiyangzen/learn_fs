# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/enam.c

Purpose: instruction mnemonic table for the MIPS backend.

Contents:
- Defines `char *anames[]`, mapping opcode enum values to assembly mnemonic strings.
- Includes all base MIPS instructions used by the backend plus Plan 9 pseudo-ops such as `DATA`, `GLOBL`, `HISTORY`, `TEXT`, `NAME`, and `SIGNAME`.
- Includes later 64-bit and conversion opcodes such as `MOVV`, `DIVV`, `TRUNCDW`, and related entries.

Integration points:
- `list.c` uses this table through `Aconv`.
- The array order must match the `enum as` in `v.out.h`.

Risks:
- Any insertion or reordering in `v.out.h` must be mirrored here exactly.
