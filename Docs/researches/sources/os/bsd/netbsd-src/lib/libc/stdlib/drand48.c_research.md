# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/drand48.c

Read completely: 32 lines.

Implements `drand48()` by returning `erand48(__rand48_seed)`. It advances and uses the global rand48 seed.

All floating conversion work is delegated to the selected `erand48()` implementation.
