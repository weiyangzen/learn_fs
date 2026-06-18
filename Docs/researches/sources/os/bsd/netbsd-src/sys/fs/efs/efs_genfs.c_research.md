# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_genfs.c

Read completely: 54 lines.

Defines the EFS `genfs_ops` table used when vnodes are initialized. It uses `genfs_size`, `genfs_gop_write`, and `genfs_gop_putrange`, while wiring allocation to `efs_gop_alloc()`.

`efs_gop_alloc()` currently returns success without allocating backing storage. This is acceptable for the read-oriented implementation but means callers should not interpret it as a real block allocation routine for writable EFS.
