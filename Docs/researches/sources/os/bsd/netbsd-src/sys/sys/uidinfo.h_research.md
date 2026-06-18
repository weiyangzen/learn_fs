# File Research: sources/os/bsd/netbsd-src/sys/sys/uidinfo.h

Read completely: 59 lines.

Declares per-UID resource accounting state and helpers.

Key elements:
- `struct uidinfo` is hash-linked by uid and tracks process count, LWP count, lock count, semaphore count, and socket buffer usage.
- Declares adjustment helpers for process, LWP, semaphore, and socket-buffer accounting.
- Declares `uid_find()` and `uid_init()`.

Risks and notes:
- Resource accounting must stay synchronized with credential/process lifecycle.
- Socket buffer accounting takes both `uidinfo` and mutable usage pointer plus `rlim_t`.
