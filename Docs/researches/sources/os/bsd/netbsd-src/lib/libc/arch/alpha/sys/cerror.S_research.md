# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/cerror.S

Alpha common syscall error handler.

Key behavior:
- Sets up GP.
- In reentrant builds, saves `ra` and `v0`, calls `__errno`, and stores the saved error value through the returned pointer.
- In non-reentrant builds, stores `v0` into global `errno`.
- Returns `-1` in `v0`.

Dependencies:
- `_REENTRANT` build mode and `__errno`.
- Alpha syscall stubs branch here on errors.
