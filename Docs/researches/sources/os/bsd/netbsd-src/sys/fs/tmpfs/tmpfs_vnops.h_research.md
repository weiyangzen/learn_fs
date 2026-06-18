# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_vnops.h

Read completely: 76 lines.

This kernel-private header declares the main tmpfs vnode operation vector pointer and all vnode operation functions implemented by `tmpfs_vnops.c`, including `tmpfs_rename` from the rename companion file.

Important interactions: included by FIFO/spec headers and tmpfs implementation files that need common vnode operation prototypes.

Security/reliability notes: no runtime logic.
