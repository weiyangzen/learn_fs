# File Research: sources/os/plan9/9front/sys/src/9/sgi/trap.c

Implements SGI/MIPS trap, interrupt, syscall, note, and register-dump handling. `trap` dispatches external interrupts, FP exceptions, TLB faults, VCEs, watchpoints, coprocessor-unusable traps, and default exceptions.

The interrupt subsystem chains handlers per MIPS interrupt level. `hpc3irqlevel` maps SGI HPC3 IRQs to MIPS interrupt levels and unmasks INT2 bits. FP handling lazily enables/restores FPU state, posts FP notes, and uses `fptrap` for selected cases.

The file also implements user notify/noted stack frames, syscall dispatch from assembly, fork/kproc child register setup, exec register setup, user PC/debug PC helpers, protected register writes for `/proc`, and diagnostic stack/register dumps.
