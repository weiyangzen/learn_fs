# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/rand.c

Implements classic `rand()`/`srand()` with a single static `u_long next` state. `rand()` advances with `next = next * 1103515245 + 12345` and returns modulo `RAND_MAX + 1`; `srand()` replaces the state.

This is simple legacy PRNG behavior, not thread-safe or suitable for security.
