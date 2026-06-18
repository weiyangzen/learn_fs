# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_mem.c

## Purpose

Implements `/proc/<pid>/mem`, allowing raw reads and writes of target process memory through procfs.

## Main Entry Point

`procfs_doprocmem()`:
- returns immediately for zero-length I/O.
- locks the target process and checks `p_candebug()`.
- delegates actual memory transfer to `proc_rwmem(p, uio)` when permitted.

## Integration Points

Registered by `procfs.c` as `mem` with `PFS_RDWR | PFS_RAW`, `procfs_attr_rw`, and `procfs_candebug`.

## Risks and Review Notes

Security is concentrated in `p_candebug()` and `proc_rwmem()`. The procfs layer itself does not add range policy beyond the caller’s `uio`.
