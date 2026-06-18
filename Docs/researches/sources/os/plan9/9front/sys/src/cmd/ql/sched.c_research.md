# File Research: sources/os/plan9/9front/sys/src/cmd/ql/sched.c

This file implements a small local instruction scheduler for PowerPC delay/stall avoidance.

Key responsibilities:
- `sched()` operates over basic blocks of up to `NSCHED` instructions when scheduling is enabled by `debug['Q']`.
- Builds side records containing each instruction, register/memory/control dependencies, memory offset/size, load markers, branch markers, and compound-instruction markers.
- Moves independent earlier instructions after loads or floating compares to avoid load-use and compare-branch stalls.
- Writes the reordered instructions back into the original `Prog` chain.

Dependency analysis:
- `regused()` computes integer register, floating register, condition/control register, and memory set/use masks.
- Tracks special resources such as LR, CTR, XER, CR fields, ICC/FCC, SB-relative memory, SP-relative memory, and generic memory.
- `depend()` prevents reordering across true, anti, output, control, and overlapping memory dependencies.
- `conflict()` detects immediate load-result use.
- `offoverlap()` refines SB/SP memory alias checks by offset and size.
- `compound()` treats multiword encodings and writes to `REGSB` as nontrivial scheduling units.

Implementation notes:
- Many special-register and FPSCR operations conservatively clobber broad state.
- Debug flag `X` prints set/use dependency masks.
