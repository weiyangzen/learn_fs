# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_fpregs.c

## Purpose

Implements `/proc/<pid>/fpregs`, exposing target-process floating-point register state through procfs raw read/write.

## Main Entry Point

`procfs_doprocfpregs()`:
- ignores nonzero offsets.
- locks the target process and requires `p_candebug()` success.
- requires the target process to be stopped with `P_SHOULDSTOP(p)` for both reads and writes.
- uses the first thread in the process.
- supports `COMPAT_FREEBSD32` by selecting `struct fpreg32` and `proc_read_fpregs32()`/`proc_write_fpregs32()` when caller and target are both ILP32.
- copies register data through `uiomove_frombuf()`.
- writes register data back only if the target is still stopped after the copy phase.

## Integration Points

Registered by `procfs.c` as `fpregs` with `PFS_RDWR | PFS_RAW`, `procfs_attr_rw`, and `procfs_candebug`.

## Risks and Review Notes

The process lock is dropped during `uiomove_frombuf()`. The code rechecks stopped state before write-back, which is critical because the process can resume while the copy is in progress.
