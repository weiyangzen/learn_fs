# File Research: sources/os/plan9/9front/sys/src/cmd/9l/sched.c

This file implements an optional local instruction scheduler for Power64 instruction blocks.

Key structures:
- `Dep` records integer registers, floating registers, condition-code effects, and condition-register effects.
- `Sch` wraps a `Prog` with dependency sets, memory offset/size, and compound-instruction metadata.

Key routines:
- `sched` builds scheduling metadata for a block, attempts to fill load-use and floating-compare delay slots with safe earlier instructions, then writes the reordered instructions back.
- `regused` computes per-instruction set/use dependencies from opcode and operand classes.
- `depend` determines whether two instructions can be interchanged without changing semantics.
- `offoverlap` detects overlapping stack/SB memory ranges.
- `conflict` detects adjacent load-result use stalls.
- `compound` treats multiword optab encodings and writes to `REGSB` as scheduling barriers.
- `dumpbits` prints dependency masks for debug output.

Important interactions:
- Called from `noop.c:noops` only when `debug['Q']` is enabled.
- Uses `oplook`, `aclass`, and `regoff` to classify operands.
- Honors marks such as `LOAD`, `BRANCH`, `FCMP`, `SYNC`, and `NOSCHED`.

Research notes:
- Memory dependencies distinguish generic memory, stack-pointer-relative memory, and static-base-relative memory.
- Special registers and FPSCR/MSR operations conservatively clobber broad dependency sets.
- The scheduler is local and bounded by `NSCHED`.
