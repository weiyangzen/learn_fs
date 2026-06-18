# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_fpregs.c

This file implements `/proc/<pid>/fpregs` access. `procfs_dofpregs()` applies exec-state, `CHECKIO`, and credential checks, reads floating-point registers into `struct fpreg`, copies them via uio, and writes them back only if the LWP is stopped.

`procfs_validfpregs()` excludes system processes.

Research notes: similar to `procfs_regs.c` and `procfs_dbregs.c`, with architecture-specific register access delegated to external helpers.
