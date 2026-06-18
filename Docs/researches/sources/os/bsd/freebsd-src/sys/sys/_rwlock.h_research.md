# File Research: sources/os/bsd/freebsd-src/sys/sys/_rwlock.h

Reader/writer lock structure definitions.

Key elements:
- Defines `struct rwlock` with common `lock_object` and volatile `rw_lock`.
- Defines cache-line-aligned `struct rwlock_padalign`.

Dependencies:
- Includes `sys/_types.h`, `sys/_lock.h`, and `machine/param.h`.

Research notes:
- The member name `rw_lock` is reserved for rwlock implementations.
- Pad-aligned form mirrors the normal layout for API compatibility.
