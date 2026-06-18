# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/noop.c

MIPS linker cleanup and scheduling-preparation pass for `vl`.

Key responsibilities:
- Strips assembler `ANOP` nodes while preserving label marks.
- Marks labels, branches, sync points, leaf functions, and scheduling boundaries.
- Computes per-TEXT frame and `BECOME` sizes, then defines `ALEFbecome`.
- Synthesizes function prologues and return/`BECOME` epilogues around MIPS stack/link-register conventions.
- Splits schedulable blocks and invokes `sched()`.
- Contains optional MIPS 24K erratum workaround logic to avoid three consecutive stores and keep stores out of delay slots.

Important behavior:
- Leaf functions with no frame avoid stack/link-save setup.
- Non-leaf returns restore link through register 2 and jump indirectly.
- Moves to/from machine or floating-control registers are forced into sync/nop-protected regions.
- `addnop()` emits the canonical MIPS zero-register `NOR` nop.

Risks:
- This is global mutable linker state; correctness depends on mark bits being maintained consistently across earlier passes.
- The 24K workaround is compiled disabled by `Mips24k = 0`.
