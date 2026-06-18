# File Research: sources/os/plan9/9front/sys/src/cmd/vl/optab.c

This file defines the MIPS instruction selection table used by the linker backend.

Key behavior:
- `optab` maps opcode plus operand classes to an `Optab.type`, emitted byte size, and default base register parameter.
- Covers text pseudo-ops, register moves, integer ALU ops, shifts, loads/stores, large constants, branches/jumps, FP ops, FP memory access, CP0/FP control moves, cache/break, case tables, and LL/SC.
- Several entries share generic forms; aliases are established later by `buildop` in `span.c`.
- The comment notes some operations are unfinished, especially some 64-bit/double memory and arithmetic combinations.

Integration and risks:
- `Optab.type` numbers are interpreted directly by `asmout`; table changes must stay synchronized.
- The table is sorted in-place by `buildop`, so code should not assume source order after initialization.
