# File Research: sources/os/plan9/9front/sys/src/cmd/kl/sched.c

This file implements local instruction scheduling for SPARC delay and hazard handling. It builds a temporary `Sch` array for a basic scheduling window, annotates each instruction with registers/condition codes/memory read/write sets, then moves independent prior instructions into branch delay slots, load-use delay slots, or floating compare delay slots.

Key functions:
- `sched()` performs the reordering and inserts nops with `addnop()` where no safe candidate exists.
- `regsused()` computes dependency masks from opcode and operand classes, including integer registers, floating registers, ICC/FCC, and coarse memory regions for generic, SB-relative, and SP-relative memory.
- `depend()` and `conflict()` decide whether instructions can be interchanged or whether a load result is immediately consumed.
- `offoverlap()` refines SB/SP memory dependency checks by byte range.
- `compound()` treats multiword encodings and writes to `REGSB` as unschedulable compounds.
- `dumpbits()` is debug output for dependency masks.

This file depends on `oplook()`, `aclass()`, `regoff()`, opcode marks such as `LOAD`, `BRANCH`, `FCMP`, and global `autosize`/`curtext`.
