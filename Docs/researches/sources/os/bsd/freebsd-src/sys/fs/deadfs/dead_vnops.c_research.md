# File Research: sources/os/bsd/freebsd-src/sys/fs/deadfs/dead_vnops.c

Read completely: 167 lines.

Purpose: implements vnode operations for dead/revoked vnodes. Deadfs gives stable behavior for file descriptors or vnodes whose backing object has gone away.

Key behavior:
- `dead_vnodeops` maps most operations to `VOP_EBADF`, `VOP_PANIC`, `VOP_NULL`, or small local handlers.
- `dead_lookup()` always returns `ENOTDIR`.
- `dead_open()` and `dead_close()` silently succeed.
- `dead_read()` returns EOF for tty vnodes and `ENXIO` otherwise.
- `dead_write()` returns `ENXIO`.
- `dead_poll()` returns `POLLHUP` plus readable bits for standard poll requests, or `POLLNVAL` for unsupported event bits.
- `dead_rename()` fails with `EXDEV` after `vop_rename_fail()`.
- `dead_getwritemount()` returns no writable mount.
- `dead_unset_text()` succeeds.

Research notes:
- Devfs uses `dead_read`, `dead_write`, and `dead_poll` for character-device vnode fallbacks.
- The file is intentionally small and defensive: dead vnodes should not perform real filesystem mutation or lookup.
