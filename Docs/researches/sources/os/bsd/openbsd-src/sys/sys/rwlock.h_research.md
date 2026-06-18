# File Research: sources/os/bsd/openbsd-src/sys/sys/rwlock.h

Defines OpenBSD reader/writer locks, recursive rwlocks, allocated rwlock objects, WITNESS integration, and status flags.

Key contents:
- Documents `rwl_owner` bit layout: wait, writer-want, write-locked, and owner/read count.
- `struct rwlock` with owner, waiter/reader counters, name, optional lock object, and trace index.
- Lock-object flag macros for normal and recursive rwlocks.
- Initializer macros with optional WITNESS data.
- Operation flags: write, read, downgrade, upgrade, interruptible, no-sleep, recurse-fail, duplicate OK.
- `struct rrwlock` for recursive writer count.

Key APIs:
- Init: `_rw_init_flags`, `rw_init*`, `_rrw_init_flags`, `rrw_init*`.
- Enter/exit/status/assertions: `rw_enter`, `rw_exit`, `rw_status`, `rw_enter_read`, `rw_enter_write`, `rw_exit_read`, `rw_exit_write`, `rw_read_held`, `rw_write_held`, `rw_lock_held`.
- Recursive variants: `rrw_enter`, `rrw_exit`, `rrw_status`.
- Allocated object lifecycle: `rw_obj_init`, `_rw_obj_alloc_flags`, `rw_obj_hold`, `rw_obj_free`.

Risk notes:
- `RW_DUPOK` and `RW_WRITE_OTHER` share the same value in different contexts; consumers must use them only in their intended APIs.
