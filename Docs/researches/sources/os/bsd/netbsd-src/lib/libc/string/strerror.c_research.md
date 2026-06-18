# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strerror.c

Implements `strerror()` and `strerror_l()` on top of `_strerror_lr()`. Threaded builds allocate a thread-specific `NL_TEXTMAX` buffer with `thr_keycreate`; non-threaded builds use a static buffer.

If thread-local allocation fails, a static fallback buffer is used. When `_strerror_lr()` reports an error such as `EINVAL` or `ERANGE`, `strerror_l()` stores that in `errno` and still returns the buffer.
