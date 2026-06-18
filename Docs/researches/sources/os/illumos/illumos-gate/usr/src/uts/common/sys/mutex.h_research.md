# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mutex.h

Public kernel mutex interface header.

Key responsibilities:
- Defines mutex types: adaptive, spin, driver, and default.
- Defines opaque `kmutex_t` layout sized differently for LP64 and ILP32.
- Under `_KERNEL`, defines cache-line padded mutex type for false-sharing-sensitive users.
- Defines `MUTEX_HELD` and `MUTEX_NOT_HELD` assertion helpers.
- Declares mutex lifecycle, enter/tryenter/exit, ownership, owner lookup, backoff tuning variables, delay hooks, synchronization, and default lock-delay helpers.

Dependencies:
- Includes `sys/types.h` outside assembly.

Notable risks:
- `kmutex_t` is intentionally opaque but ABI-sized; changing its storage breaks kernel consumers.
- Spin mutex initialization depends on correct interrupt block cookie use.
