# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/rwlock_emul.c

Single-thread read/write lock emulation/debug checker.

Key behavior:
- Tracks magic value, owner, read/write hold counts, and source location.
- Read/write enter abort if already held.
- Downgrade converts one write hold to one read hold.
- Exit requires exactly one read or write hold.
- Init/destroy maintain a global `initcount`; `ipf_rwlock_clean()` aborts on leaks.

Research notes:
- `eMrwlock_try_upgrade()` currently aborts if a read lock is held, so it does not model a normal upgrade from read to write.
