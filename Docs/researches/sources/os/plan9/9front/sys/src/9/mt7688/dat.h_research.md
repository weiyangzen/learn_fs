# File Research: sources/os/plan9/9front/sys/src/9/mt7688/dat.h

MT7688 MIPS machine data definitions. It defines Plan 9 configuration structures, MIPS FP emulator save state, process FPU state, process MMU PID state, Mach fields, KMap, software TLB entries, active CPU state, and hardware device config structures.

`FPsave` includes emulated FP register bits, control/status, delay-slot execution tracking, and stuck-fault detection fields. `Mach` includes soft-TLB state, process pointer, interrupt PC, TLB fault counters, PID ownership, kmap tracking, timer counters, CPU speed/delay fields, and stack.

Notable risks: comments mark legacy MIPS AOUT/boot magic handling; the FP and TLB structures are tightly coupled to MIPS trap/MMU code outside this group.
