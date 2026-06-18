# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_dbregs.c

## Purpose

Implements `/proc/<pid>/dbregs`, exposing target-process debug registers through procfs raw read/write.

## Main Entry Point

`procfs_doprocdbregs()`:
- ignores nonzero offsets by returning success with no data.
- locks the target process and verifies `p_candebug()`.
- selects the first thread in the process.
- under `COMPAT_FREEBSD32`, wraps 32-bit callers to 32-bit debug register access only when the target process is also ILP32; otherwise returns `EINVAL`.
- reads debug registers with `proc_read_dbregs()` or `proc_read_dbregs32()`.
- copies the register buffer through `uiomove_frombuf()`.
- on write, requires the process to be stopped via `P_SHOULDSTOP(p)` before calling `proc_write_dbregs()` or `proc_write_dbregs32()`.

## Integration Points

Registered by `procfs.c` as `dbregs` with `PFS_RDWR | PFS_RAW`, `procfs_attr_rw`, and `procfs_candebug`.

## Risks and Review Notes

Reads do not require the target to be stopped, while writes do. The code unlocks the process around `uiomove_frombuf()` and relocks afterward, so stopped/debuggability state can change between read-copy and write-back; the write path rechecks stopped state but not `p_candebug()` after relock.
