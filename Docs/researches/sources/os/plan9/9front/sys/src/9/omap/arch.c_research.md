# File Research: sources/os/plan9/9front/sys/src/9/omap/arch.c

This ARM OMAP architecture helper file contains miscellaneous process/register support routines. It is explicitly described as a temporary dumping ground for architecture-dependent pieces.

It implements `setkernur`, `evenaddr`, `userpc`, `setregisters`, `kprocchild`, `dbgpc`, FP process hooks (`procsetup`, `procfork`, `procsave`, `procrestore`), `userureg`, and a simple `cas32` using `splhi` rather than hardware atomic instructions.

Filesystem relevance is through generic kernel support: `evenaddr` is called from syscall/file code for alignment checks, `setregisters` affects `/proc` register writes, and process setup/save/restore affects filesystem server process scheduling.

Notable risks: `cas32` is only interrupt-safe on the local CPU and not a scalable SMP atomic primitive; a TODO notes VFPv3 state is not saved/restored with newer registers.
