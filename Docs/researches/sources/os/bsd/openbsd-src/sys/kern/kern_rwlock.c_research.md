# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_rwlock.c

Purpose: Implements OpenBSD reader/writer locks, recursive rwlocks, WITNESS integration, diagnostics, and dynamically allocated rwlock objects.

Key behavior:
- Lock owner state encodes writer ownership or reader count in `rwl_owner`.
- Writers use CAS, optional MP spinning, waiters count, sleeps on `rwl_waiters`, and wake one writer before readers.
- Readers acquire directly when no writer and no waiters, otherwise sleep on `rwl_readers`.
- `rw_exit_read()` and `rw_exit_write()` validate ownership and call `rw_exited()` to wake waiters/readers.
- `rw_enter()` multiplexes read, write, downgrade, and no-sleep upgrade operations.
- `rw_status()` distinguishes unlocked, read-held, write-held by current thread, and write-held by another thread.

Concurrency details:
- Uses memory barriers around atomic owner transitions.
- Avoids spinning while holding the kernel lock.
- Supports interruptible sleeps via `RW_INTR`.
- WITNESS tracks lock ordering and assertions when enabled.

Recursive and object locks:
- `rrw_enter()` allows recursive write ownership and tracks `rrwl_wcnt`.
- `rrw_exit()` unwinds recursive holds before releasing the base rwlock.
- `rw_obj_init()`, `_rw_obj_alloc_flags()`, `rw_obj_hold()`, and `rw_obj_free()` manage pooled refcounted rwlock objects.

Filesystem relevance:
- This is a shared synchronization primitive used by VFS, process, resource-limit, and device paths. Correct wake ordering and ownership checks are foundational for filesystem concurrency.
