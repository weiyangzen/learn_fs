# File Research: sources/os/plan9/9front/sys/src/9/sgi/faultmips.c

Handles MIPS page/address faults and alignment validation. `faultmips` converts MIPS TLB exception causes into Plan 9’s common `fault` call, posts user notes on unrecoverable user faults, and panics with register dumps on kernel faults.

`tstbadvaddr` decodes the faulting MIPS load/store instruction to check whether `badvaddr` matches the computed effective address, including branch-delay handling. Debug-only stuck-fault tracking records repeated faults at the same VA/PC/pid/cause.

`validalign` relaxes 64-bit alignment to 32-bit alignment for this 32-bit OS/compiler environment, then posts `"sys: odd address"` on invalid alignment.
