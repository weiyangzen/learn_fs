# File Research: sources/os/plan9/9front/sys/src/cmd/vl/noop.c

This file rewrites pseudo-instructions, marks scheduling boundaries, inserts stack-frame prologues/epilogues, expands returns, and invokes local instruction scheduling.

Key behavior:
- `noops` finds leaf functions, frame sizes, BECOME requirements, labels, sync points, branch targets, and strips `ANOP`.
- Expands `ATEXT` into stack adjustment and link-register save when needed.
- Expands ordinary `ARET` into restore/stack-adjust/jump sequences, with special handling for leaf functions.
- Expands BECOME-style returns from `RET $n`.
- Marks hard scheduling barriers for control transfer, system/TLB/case operations, special CP0/FP control moves, and cache-sensitive sequences.
- Splits instruction stream into schedulable blocks and calls `sched`.
- `addnop` inserts canonical MIPS NOP (`NOR R0,R0,R0`); `nocache` clears cached optab/class fields.

Integration and risks:
- Depends on `curtext`, `autosize`, and `Sym.frame/become` metadata later consumed by codegen.
- Must preserve delay-slot and scheduling correctness around branches, returns, and special registers.
