# File Research: sources/os/plan9/9front/sys/src/9/sgi/mmu.c

Implements SGI/MIPS TLB and kmap management. It invalidates hardware TLB entries, manages a fixed `KMap` pool, maintains per-Mach active kmaps, assigns TLB PIDs to processes, populates a software TLB cache, and handles kmap faults.

`kmap` maps physical pages into KSEG3 while preserving cache-color bits to avoid virtual coherence exceptions. `putstlb` updates the hashed soft-TLB entry used by the assembly fast miss path; `putmmu` updates both soft and hardware TLB, including text-cache flush when needed.

`purgetlb` invalidates stale process ASIDs, clears dead soft-TLB entries, and invalidates hardware entries whose PID no longer maps to a live process. `mmuswitch` uses TLB entry 0 to establish current PID.
