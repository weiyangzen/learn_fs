# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/abort.c

Read completely: 84 lines.

Implements `abort()`. It unblocks `SIGABRT` while blocking other signals, flushes stdio through `__cleanup` once, raises `SIGABRT`, then if a handler returns or the signal was ignored, resets `SIGABRT` to default, raises it again, and finally calls `_exit(1)`.

A static `aborting` flag prevents recursive cleanup if `abort()` is invoked from a `SIGABRT` handler.
