# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strtok.c

Implements non-reentrant `strtok()` as a thin wrapper around `strtok_r()` with a static saved pointer.

This inherits `strtok`’s normal process-global state and thread-unsafety.
