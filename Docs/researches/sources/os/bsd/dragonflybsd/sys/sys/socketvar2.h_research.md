# File Research: sources/os/bsd/dragonflybsd/sys/sys/socketvar2.h

This kernel-only inline header defines locking and atomic state helpers for `signalsockbuf` and sockets.

Key responsibilities:
- Rejects userland inclusion.
- Includes `socketvar.h`, `systm.h`, and machine atomics.
- Defines `ssb_lock()` inline when `MALLOC_DEFINE` is present:
  - spins/CASes `SSB_LOCK`
  - uses `_ssb_lock()` when lock is held and waiting is allowed
  - returns `EWOULDBLOCK` for non-waiting lock failure
  - acquires `ssb_token` on success
- Defines `ssb_unlock()`:
  - releases token
  - clears `SSB_LOCK` and `SSB_WANT`
  - wakes waiters if `SSB_WANT` was set
- Defines atomic socket state helpers:
  - `sosetstate()`
  - `soclrstate()`
- Defines `soreference()` to increment `so_refs`.

Important invariants:
- `ssb_lock()` must acquire both the flag lock and the lwkt token on success.
- `ssb_unlock()` asserts the lock bit is held before releasing.
- `soreference()` allows a 0 to 1 transition for aborted sockets left on accept queues.

Research notes:
- This file keeps fast-path socket locking and state transitions inline while relying on slower contested code elsewhere.
