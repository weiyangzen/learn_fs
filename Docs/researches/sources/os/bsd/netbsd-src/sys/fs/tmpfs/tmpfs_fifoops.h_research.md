# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_fifoops.h

Read completely: 53 lines.

This kernel-private header declares the tmpfs FIFO vnode operation vector pointer and the FIFO-specific close/read/write wrappers.

Important interactions: included by `tmpfs_fifoops.c` and `tmpfs_subr.c`, where FIFO nodes are assigned `tmpfs_fifoop_p`.

Security/reliability notes: no runtime logic.
