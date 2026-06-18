# File Research: sources/os/bsd/openbsd-src/sys/miscfs/deadfs/dead_vnops.c

Purpose: Defines vnode operations for dead/revoked vnodes after the underlying object has been invalidated.

Key behavior:
- `dead_vops` maps most namespace-changing operations to generic bad operations and most data/metadata operations to `EBADF`.
- `dead_open()` fails with `ENXIO`.
- `dead_read()` returns EOF for tty vnodes and `EIO` otherwise; `dead_write()` returns `EIO`.
- `dead_ioctl()`, `dead_strategy()`, and `dead_bmap()` may forward to the underlying vnode operation only after `chkvnlock()` indicates the vnode is stable.
- `dead_kqfilter()` supports read/write/poll exception filters through `dead_filtops`.
- `dead_inactive()` unlocks the vnode; `dead_lock()` waits through `VXLOCK` transitions and forwards locks when still possible.
- `chkvnlock()` waits while `VXLOCK` is set, setting `VXWANT` as needed.

Filesystem relevance:
- Provides safe behavior for file descriptors and buffers that outlive device revoke or vnode teardown.
- Prevents stale vnode operations from reaching normal filesystem logic except selected guarded forwarding paths.
