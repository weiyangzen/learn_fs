# File Research: sources/os/plan9/9front/sys/src/cmd/ql/optab.c

This file defines the instruction selection table for `ql`.

Contents:
- `Optab optab[]` maps assembler opcodes plus operand classes to:
  - encoding type used by `asmout()`,
  - instruction size in bytes,
  - default base register parameter.
- Covers text pseudo-ops, moves, arithmetic, logical operations, loads/stores, branches, condition branches, floating-point operations, SPR/MSR/FPSCR/CR moves, trap/cache/TLB operations, string load/store, and embedded/FP2 PowerPC opcodes.
- The final sentinel is `{ AXXX, ... }`.

Usage:
- `span.c` sorts and indexes this table in `buildop()`.
- `oplook()` uses `oprange` plus operand class compatibility to select the matching row.
- `asmout.c` interprets the selected row’s `type` and `size`.

Implementation notes:
- Many opcode families are represented once here and then aliased in `buildop()`.
- The table is highly coupled to `aclass()` classifications and `asmout()` type cases.
- Incorrect sizes here would corrupt PC layout, branch reach checks, and output emission.
