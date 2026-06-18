# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zrlock.h

Defines a small reference-style lock with wait-for-zero behavior and optional debug owner tracking.

Key elements:
- `zrlock_t` contains mutex, volatile refcount, condition variable, padding, and debug owner/caller fields under `ZFS_DEBUG`.
- Declares init/destroy, add/remove, tryenter/exit, zero check, locked check, and debug owner accessor.
- `zrl_add()` macro passes `__func__` to `zrl_add_impl()`.

Main dependencies and interactions:
- Includes `zfs_context.h`.
- Used where subsystems need to prevent teardown until reference count reaches zero.

Implementation notes:
- The debug caller capture helps identify the ref holder in diagnostics.
