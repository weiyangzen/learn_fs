# File Research: sources/os/plan9/plan9/sys/src/cmd/ka/l.s

Despite living under `cmd/ka`, this file is SPARC kernel assembly support code, not assembler implementation code. It defines low-level Plan 9 SPARC constants and routines used by the kernel/runtime.

The top half defines memory layout, page/MMU constants, PSR bits, special registers, kernel/user virtual address ranges, MMU segment/PMEG constants, PTE bits, ASI addresses, and boot/trap addresses.

`start` and `startvirt` set up early virtual mapping, stack, PSR, floating-point constants, SB, MACH, WIM, and branch into `main`. Other routines implement atomic swap variants, interrupt priority control (`spllo`, `splhi`, `splx`), user transition, trap/syscall linkage, register save/restore, special register accessors, MMU/ASI byte/word access helpers, and FP register save/restore.

The file exports globals `mach0`, `fpq`, and `fsr`. It is architecture-critical and assumes SPARC register conventions such as `R6` for `m->` and `R5` for `u->`.
