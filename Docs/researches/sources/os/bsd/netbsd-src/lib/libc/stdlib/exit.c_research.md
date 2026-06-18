# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/exit.c

Read completely: 65 lines.

Implements `exit(int status)`. In libc builds, it first runs thread-local C++ destructors if registered, then calls `__cxa_finalize(NULL)` for global exit handlers. It then runs stdio cleanup via `__cleanup` if present and finally calls `_exit(status)`.

The file also defines the global `void (*__cleanup)(void)` hook used by stdio and `abort()`.
