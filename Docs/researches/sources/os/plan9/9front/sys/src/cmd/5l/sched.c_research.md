# File Research: sources/os/plan9/9front/sys/src/cmd/5l/sched.c

This file implements a local instruction scheduler for `5l`, focused on avoiding ARM load, branch, and floating-compare stalls by reordering instructions or inserting NOPs.

Key elements:
- `Sch` wraps a `Prog` plus computed dependency sets, memory offset/size, NOP count, and compound-instruction flag.
- `Dep` stores integer register, floating register, and condition/memory dependency bitsets.
- `sched()` builds scheduling metadata for a basic block, runs prepasses to group independent loads and move useful instructions near loads, then fills delay/stall slots or inserts NOPs.
- `regused()` computes used/set dependency bits from opcode and operand classes.
- `depend()` determines whether two instructions may be interchanged.
- `conflict()` checks adjacent hazard conflicts.
- `offoverlap()` determines memory overlap for stack/SB-offset references.
- `compound()` treats multiword optab forms or writes to `REGSB` as compound.
- `dumpbits()` prints dependency sets for debug output.

Dependencies and integration:
- Uses `aclass()`, `regoff()`, `oplook()`, `addnop()`, and `Count nop` globals from the larger linker.
- Operates on `Prog` sequences after earlier rewriting and before final emission.

Notable behavior:
- Memory dependencies distinguish generic memory, SP-relative memory, and SB-relative memory.
- Loads from the same hardware-like address are not allowed to pass each other.
- It counts missed scheduling opportunities in verbose mode.
- It may insert two NOPs for PSR use-then-set hazards.

Research notes:
- This scheduler is conservative and local; it avoids changing semantics with bitset dependency checks rather than global analysis.
