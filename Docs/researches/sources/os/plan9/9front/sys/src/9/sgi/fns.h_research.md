# File Research: sources/os/plan9/9front/sys/src/9/sgi/fns.h

Machine-dependent function declarations and address macros for the SGI/MIPS port. It includes ARCS console calls, clock, cache, MMU/TLB, FP, trap, interrupt, process, screen, and utility prototypes.

Defines `KADDR`, `PADDR`, and `KSEG1ADDR` conversions, plus `userureg`. The file is the declaration bridge between C files and low-level assembly routines in `l.s`.
