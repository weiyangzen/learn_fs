# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_regs.c

## Purpose

Implements `/proc/<pid>/regs`, exposing target-process general register state through procfs raw read/write.

## Main Entry Point

`procfs_doprocregs()`:
- ignores nonzero offsets.
- requires `p_candebug()` success.
- requires `P_SHOULDSTOP(p)` for register read and write.
- selects the first thread in the process.
- supports `COMPAT_FREEBSD32` with `struct reg32` and 32-bit read/write routines when caller and target are both ILP32.
- copies register state through `uiomove_frombuf()`.
- writes back the register state only if the target remains stopped.

## Integration Points

Registered by `procfs.c` as `regs` with `PFS_RDWR | PFS_RAW`, `procfs_attr_rw`, and `procfs_candebug`.

## Risks and Review Notes

The stopped-state requirement prevents racing active execution. Like the fpregs handler, the process lock is dropped for the user I/O copy and stopped state is rechecked before write-back.
