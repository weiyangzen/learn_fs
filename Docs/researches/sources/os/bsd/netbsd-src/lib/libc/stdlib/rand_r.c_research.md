# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/rand_r.c

Implements `rand_r(unsigned int *seed)` as the reentrant form of the simple `rand()` LCG. It updates the caller-provided seed with `*seed * 1103515245 + 12345` and masks the result with `RAND_MAX`.

The caller owns synchronization and seed storage.
