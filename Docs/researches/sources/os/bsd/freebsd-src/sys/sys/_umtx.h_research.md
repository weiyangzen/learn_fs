# File Research: sources/os/bsd/freebsd-src/sys/sys/_umtx.h

User mutex and synchronization object ABI structures.

Key elements:
- Defines `struct umtx`, `umutex`, `ucond`, `urwlock`, `_usem`, `_usem2`, and `_umtx_time`.
- Includes owner fields, flags, robust linkage, waiter counters, semaphore counts, and timeout metadata.

Dependencies:
- Includes `sys/_types.h` and `sys/_timespec.h`.

Research notes:
- These layouts are user/kernel ABI for FreeBSD thread synchronization primitives.
- 32-bit padding is explicit in `struct umutex`.
