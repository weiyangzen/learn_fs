# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/sched.c

Optional local instruction scheduler for PowerPC delay/stall reduction.

Core model:
- `Sch` wraps one `Prog` with dependency sets, memory offset/size, and compound flags.
- `Dep` tracks integer regs, floating regs, condition/control bits, and memory categories.
- `regused()` classifies each instruction’s read/write effects based on opcode and operand classes.
- `depend()` determines whether two instructions can be interchanged safely.
- `conflict()` detects immediate load/use or compare/branch hazards.
- `offoverlap()` refines SP/SB memory dependencies using offset/size ranges.
- `compound()` treats multiword instruction expansions and writes to `REGSB` as unschedulable compounds.
- `sched()` builds a fixed-size scheduling window, moves safe earlier instructions between load/use or fcmp/branch pairs, and writes the reordered `Prog` data back.

It is only active under debug flag `Q`, invoked from `noops()` over bounded basic blocks.

Risk/notes:
- Memory disambiguation is conservative except for SP/SB offset ranges.
- Special registers and broad operations set all dependency classes to prevent unsafe movement.
- Scheduler relies on `aclass()` and `oplook()` from `span.c`, so instruction selection must be initialized first.
