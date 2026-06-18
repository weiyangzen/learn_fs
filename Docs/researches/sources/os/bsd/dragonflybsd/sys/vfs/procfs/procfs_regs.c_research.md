# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_regs.c

This file implements `/proc/<pid>/regs` access. `procfs_doregs()` rejects execing targets, enforces `CHECKIO` and credential checks, reads general registers into `struct reg`, copies through the uio, and writes back only when the process is stopped.

`procfs_validregs()` excludes system processes.

Research notes: unlike FP/debug register files, the stopped check uses process state `SSTOP` rather than `lp->lwp_stat`.
