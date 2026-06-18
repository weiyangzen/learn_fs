# File Research: sources/os/bsd/freebsd-src/sys/sys/_lockmgr.h

Private lockmgr structure definition.

Key elements:
- Defines `struct lock` containing `lock_object`, volatile `lk_lock`, sleep-failure priority fields, timeout, and optional debug stack.
- Includes stack storage only when `DEBUG_LOCKS` is enabled.

Dependencies:
- Optionally includes `sys/_stack.h`.
- Requires `struct lock_object` to be visible from including context.

Research notes:
- Lockmgr locks are used by older VFS/filesystem paths.
- Structure layout is conditional on lock debugging.
