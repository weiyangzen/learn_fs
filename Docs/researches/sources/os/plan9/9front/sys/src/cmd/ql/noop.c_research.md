# File Research: sources/os/plan9/9front/sys/src/cmd/ql/noop.c

This file performs late pseudo-instruction cleanup, function prologue/epilogue generation, leaf detection, and optional scheduling boundaries.

Key responsibilities:
- `noops()` scans the instruction stream to:
  - detect leaf functions,
  - compute frame and become sizes,
  - strip `ANOP`,
  - mark labels, branches, sync instructions, floating instructions, and scheduling barriers,
  - expand `ARETURN`,
  - expand Plan 9 `BECOME` pseudo-returns,
  - insert stack adjustment and link-register save/restore code.
- Updates symbol metadata for function frame and become requirements.
- Defines `ALEFbecome` with the maximum become frame requirement.
- Invokes `sched()` over eligible basic blocks when `debug['Q']` enables scheduling.
- `addnop()` inserts a PowerPC no-op as `NOR R0,R0`.

Important behavior:
- Leaf functions with no stack frame suppress save/restore code and become `SLEAF`.
- Non-leaf prologues save LR through `REGTMP` and use `MOVWU` when the stack adjustment is small.
- Returns are rewritten into LR restore, stack restore, and branch-to-LR sequences.

Implementation notes:
- Many low-level or ordering-sensitive instructions are marked `SYNC` and excluded from unsafe scheduling movement.
- Branch targets skip over stripped NOPs and are marked as labels.
