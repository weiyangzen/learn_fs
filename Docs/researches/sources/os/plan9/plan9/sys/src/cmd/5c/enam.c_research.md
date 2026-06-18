# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/enam.c

Opcode-name table for the ARM compiler backend.

Key contents:
- `anames[]` maps `enum as` opcode numbers from `5.out.h` to printable mnemonic strings.
- Includes integer, branch, FP, move, pseudo-op, multiply-long, branch-exchange, exclusive load/store, and sentinel names.

Notes:
- Must stay aligned with the opcode enum; used by listing/debug formatting.
