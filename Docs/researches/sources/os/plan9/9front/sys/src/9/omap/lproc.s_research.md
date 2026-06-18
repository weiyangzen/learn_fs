# File Research: sources/os/plan9/9front/sys/src/9/omap/lproc.s

Process-transition assembly helpers.

Key behavior:
- `touser` performs the first transition to user mode by installing the user stack pointer, setting SPSR to user mode, stacking the user PC (`UTZERO+0x20`), and returning from exception.
- `forkret` restores a saved `Ureg` frame for a newly forked process and returns through `RFE`.

Research notes:
- Comments explain Plan 9 assembler `RFE` semantics as a pre-v6 return-from-exception simulation.
