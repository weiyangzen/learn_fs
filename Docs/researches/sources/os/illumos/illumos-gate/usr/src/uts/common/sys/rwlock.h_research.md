# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rwlock.h

## Role

`rwlock.h` declares the public kernel/DDI readers-writer lock interface.

## Types

`krw_type_t` distinguishes DDI driver rwlocks from default kernel rwlocks.

`krw_t` identifies requested mode:
- writer.
- reader.
- reader that may starve writers.

`krwlock_t` is opaque, represented as one pointer-sized opaque slot.

## Kernel API

Under `_KERNEL`, the header declares:
- init/destroy: `rw_init()`, `rw_destroy()`.
- enter/try/exit: `rw_enter()`, `rw_tryenter()`, `rw_exit()`.
- mode changes: `rw_downgrade()`, `rw_tryupgrade()`.
- state queries: `rw_read_held()`, `rw_write_held()`, `rw_lock_held()`, `rw_read_locked()`, `rw_iswriter()`, `rw_owner()`.
- backoff/delay hooks: `rw_lock_backoff`, `rw_lock_delay`.

Convenience macros map `RW_READ_HELD`, `RW_WRITE_HELD`, `RW_LOCK_HELD`, and `RW_ISWRITER`.

## Research Notes

This is a core kernel synchronization ABI. The implementation layout is hidden here and exposed only in `rwlock_impl.h`.
