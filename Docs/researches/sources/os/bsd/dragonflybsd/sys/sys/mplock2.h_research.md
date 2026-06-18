# File Research: sources/os/bsd/dragonflybsd/sys/sys/mplock2.h

Inline macro wrapper for DragonFlyBSD's legacy MP lock, implemented as an LWKT token.

Key responsibilities:
- Maps MP lock operations to `mp_token` token operations:
  - `get_mplock()`
  - `try_mplock()`
  - `rel_mplock()`
  - `get_mplock_count(td)`
- Declares `cpu_get_initial_mplock()`.
- Provides `MP_LOCK_HELD()` and `ASSERT_MP_LOCK_HELD()` helpers.

Important behavior:
- `try_mplock()` returns non-zero on success, matching `lwkt_trytoken()`.
- The lock is represented as exclusive ownership of `mp_token`.

Dependencies:
- Includes machine atomic operations, `thread.h`, and `globaldata.h`.
- Depends on LWKT token APIs/macros and global `mp_token`.

Notable risks:
- This is a compatibility synchronization boundary; callers must understand whether their subsystem is still MP-lock protected or independently MPSAFE.
- Misinterpreting the success convention of `try_mplock()` can invert lock handling.
