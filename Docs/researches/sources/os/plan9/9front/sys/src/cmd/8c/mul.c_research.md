# File Research: sources/os/plan9/9front/sys/src/cmd/8c/mul.c

This file optimizes multiplication by constants for the 386 compiler backend.

Key responsibilities:
- Searches compact shift/add/sub algorithms for a constant multiplier in `mulparam()`.
- Caches recent multiplier plans in `multab`.
- `lowbit()` finds the lowest set bit in a constant.
- `genmuladd()` emits LEA/index-address based multiply-add patterns.
- Helper tables/functions `m0()`, `m1()`, and `m2()` map small algorithm constants to x86 scale factors.
- `shiftit()` emits shift-left or add-doubling for small shifts.
- `mulgen()` emits optimized constant multiplication when possible, otherwise falls back to normal multiply.

Integration points:
- Called from `cgen.c` and `cgen64.c`.
- Uses `gopcode()`, `gins()`, `gmove()`, `regalloc()`, and `regfree()` from `txt.c`.
- Relies on x86 scaled-index addressing for efficient LEA sequences.

Risks and invariants:
- Algorithm selection is cost-based and limited to a hand-coded set of patterns.
- Invalid mapping in `m0`/`m1`/`m2` triggers diagnostics but would indicate internal table corruption.
