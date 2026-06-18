# File Research: sources/os/plan9/9front/sys/src/cmd/vl/sched.c

This file implements local instruction scheduling for MIPS delay slots and load/use hazards.

Key behavior:
- Builds `Sch` side records for up to `NSCHED` instructions with integer, floating, condition/special-register, and memory dependency sets.
- `regsused` classifies source/destination operands, load markers, branch/fcmp markers, memory offsets/sizes, HI/LO, CP0, FP control, and atomic LL/SC constraints.
- `sched` performs a prepass to group non-conflicting loads and find filler instructions, then tries to fill load/branch/fcmp delay slots or inserts NOPs.
- Tracks delay-slot statistics for load, branch, fcmp, and HI/LO hazards.
- `depend`, `conflict`, and `offoverlap` enforce scheduling safety, including same-address device-load ordering and atomic instruction barriers.
- `compound` treats multiword emissions and writes to `REGSB` as nontrivial for scheduling.

Integration and risks:
- Depends on accurate operand classes from `aclass` and instruction sizes from `oplook`.
- Conservative memory dependency rules are important for MMIO-like loads and stack/global aliasing.
