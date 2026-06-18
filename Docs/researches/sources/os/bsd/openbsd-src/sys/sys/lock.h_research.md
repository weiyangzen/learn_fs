# File Research: sources/os/bsd/openbsd-src/sys/sys/lock.h

Compatibility wrapper mapping old `LK_*` lock flags onto OpenBSD rwlock flags.

Key contents:
- Includes `<sys/rwlock.h>`.
- Maps `LK_EXCLUSIVE`, `LK_SHARED`, `LK_NOWAIT`, `LK_RECURSEFAIL`, and `LK_EXCLOTHER` to corresponding `RW_*` values.
- Adds legacy-specific `LK_DRAIN` and `LK_RETRY`.

Integration:
- Used by VFS/vnode locking code that still names lock operations with `LK_*`.
