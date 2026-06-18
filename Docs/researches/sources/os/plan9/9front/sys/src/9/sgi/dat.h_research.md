# File Research: sources/os/plan9/9front/sys/src/9/sgi/dat.h

Defines SGI/MIPS machine-dependent data structures consumed by the portable Plan 9 kernel and assembler. It includes `Conf`, `Confmem`, `Label`, `ISAConf`, floating-point save state, process MMU state, `Mach`, `KMap`, and software TLB entries.

Important ABI constraint: the leading fields of `Mach` are fixed for `l.s` and cannot move. The file defines per-Mach TLB PID ownership, active kmaps, timer accounting, delay calibration, and soft-TLB collision stats.

Also defines global `active`, register globals `m` and `up`, and MIPS-specific `KMap`/`Softtlb` structures used by `mmu.c` and the assembly TLB miss path.
