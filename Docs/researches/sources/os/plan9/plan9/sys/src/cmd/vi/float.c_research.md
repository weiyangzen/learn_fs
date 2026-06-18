# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/float.c

Purpose: Implements MIPS COP1 floating-point instruction simulation.

Key behavior:
- Defines the COP1 function table for arithmetic, moves, conversions, and comparisons.
- Handles single, double, and word formats with register format tracking.
- Implements `lwc1`, `swc1`, `mfc1`, `mtc1`, branch-on-FP-condition, arithmetic ops, abs/neg/move, conversions, and condition comparisons.
- Sets or clears the FP condition bit in `fpsr` according to compare predicates and NaN handling.

Dependencies:
- Uses MIPS register state, memory accessors, instruction decode macros, tracing, and `isNaN`.

Notable details:
- Many COP1 operations are deliberately unimplemented and trap through `unimp`.
- Double register byte/word ordering is adjusted through register format state.
