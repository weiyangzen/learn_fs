# File Research: sources/os/bsd/netbsd-src/lib/libc/include/atexit.h

Private libc declarations for C++ ABI and thread-local exit handlers.

Declares:
- `__cxa_atexit`
- `__cxa_finalize`
- `__cxa_thread_run_atexit`
- `__cxa_thread_atexit`

When `_LIBC` is defined, exposes hidden boolean `__cxa_thread_atexit_used`.
