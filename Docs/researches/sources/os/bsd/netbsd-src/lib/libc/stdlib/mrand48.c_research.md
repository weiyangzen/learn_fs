# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/mrand48.c

Implements `mrand48()` for the global 48-bit LCG state. It advances `__rand48_seed` with `__dorand48()` and returns the signed high 32 bits assembled from seed words 2 and 1.

This is part of the shared `rand48.h` internal state family and provides a weak alias to `_mrand48`.
