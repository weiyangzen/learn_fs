# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vdprintf.c

Implements `vdprintf_l()` and `vdprintf()`. It validates that the fd fits in stdio’s short `_file` storage, verifies the descriptor is writable with `fcntl(F_GETFL)`, builds a stack `FILE` around the fd and a `BUFSIZ` buffer, then calls `vfprintf_l()` and flushes.

The fake stream uses `__swrite` and has no close callback, so the caller’s fd remains open. Invalid access mode returns `EOF` with `EINVAL`.
