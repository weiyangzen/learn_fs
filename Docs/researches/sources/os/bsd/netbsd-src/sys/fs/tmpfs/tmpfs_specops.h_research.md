# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_specops.h

Read completely: 53 lines.

This kernel-private header declares the tmpfs special-device vnode operation vector pointer and close/read/write wrappers.

Important interactions: included by `tmpfs_specops.c` and `tmpfs_subr.c`.

Security/reliability notes: no runtime logic.
