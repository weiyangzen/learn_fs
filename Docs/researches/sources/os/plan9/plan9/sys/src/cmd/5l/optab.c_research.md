# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/optab.c

## Scope

ARM linker opcode selection table.

## Contents

- Defines `optab[]`, the data table mapping abstract `Prog` instructions and operand classes to encoding type, output size, base register parameter, and flags.
- Covers text pseudo-ops, integer ALU, immediate moves, branches, shifts, SWI, words, byte/halfword moves, multiply/divide pseudo-ops, load/store classes, PSR moves, MOVM, SWP, RFE, old FPA, VFP, case tables, relocatable absolute loads/stores, and ARMv4 halfword forms.
- Flags such as `LFROM`, `LTO`, `LPOOL`, `V4`, and `VFP` direct literal pool and architecture-specific handling.

## Dependencies

Consumed by span/buildop/oplook logic and `asmout()` in `asm.c`.

## Risks And Invariants

- Table order and specificity matter for opcode selection.
- Encoding `type` numbers must match `asmout()` cases exactly.
- Architecture flags must match command-line/default `armv4` and `vfp` configuration.
