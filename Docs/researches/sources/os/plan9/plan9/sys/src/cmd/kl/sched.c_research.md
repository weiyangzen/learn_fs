# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/sched.c

Read fully: 672 lines, 10796 bytes. SHA-256 prefix: `8bab760459cf4c11`.

This is the local instruction scheduler for SPARC delay slots and hazards. It models a bounded block as `Sch` entries containing a copied `Prog`, sets/uses dependency masks, memory offset/size, and flags for inserted nops or compound instructions.

`sched()` builds side structures for a block, then scans backward to:
- fill branch delay slots with earlier safe instructions,
- separate load/use pairs when a non-conflicting instruction is available,
- handle floating compare followed by branch delays,
- insert nops when no safe fill exists.

`regsused()` classifies instruction dependencies over integer registers, floating registers, condition codes, and memory spaces (`MEM`, `SP`, `SB`). `depend()`, `conflict()`, and `offoverlap()` decide reorder safety. `compound()` treats multiword encodings and `REGSB` writes as not freely movable.

Integration: called by `noops()` for block ranges split by labels, branches, sync instructions, and scheduler-size limits. Uses `aclass()`, `regoff()`, and `oplook()` from `span.c`.

Risk notes: memory aliasing is conservative but offset-based only within recognized SP/SB spaces. Compound instruction detection depends on final `Optab.size`.
