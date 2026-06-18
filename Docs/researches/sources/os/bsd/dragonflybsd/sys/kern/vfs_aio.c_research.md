# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_aio.c

## Purpose

`vfs_aio.c` is a stub implementation for the POSIX 1003.1B AIO/LIO facility in DragonFly BSD. It provides syscall entry points and a kqueue filterops symbol, but no asynchronous I/O functionality.

## Main Responsibilities

- Defines syscall handlers for AIO/LIO-related system calls.
- Returns `ENOSYS` from every AIO syscall stub.
- Provides `aio_filtops` for event-filter integration.
- Rejects AIO filter attachment with `ENXIO`.

## Implemented Entry Points

The following syscall handlers all immediately return `ENOSYS`:

- `sys_aio_return()`
- `sys_aio_suspend()`
- `sys_aio_cancel()`
- `sys_aio_error()`
- `sys_aio_read()`
- `sys_aio_write()`
- `sys_lio_listio()`
- `sys_aio_waitcomplete()`

The source tree's syscall table references these handlers for AIO syscall numbers, so userland can call the symbols but receives "function not implemented" behavior.

## Event Filter Behavior

`filt_aioattach()` always returns `ENXIO`, indicating that an AIO knote cannot be attached. `aio_filtops` is exported with `FILTEROP_MPSAFE`, the attach function, and null detach/event callbacks.

## Integration and Risk Notes

This file deliberately contains no VFS, vnode, buffer, credential, request queue, signal, completion, cancellation, or timeout logic. Its behavior is stable and small: AIO is unavailable through these interfaces. Compatibility-sensitive callers must handle `ENOSYS` for syscalls and `ENXIO` for kqueue AIO filter attachment.
