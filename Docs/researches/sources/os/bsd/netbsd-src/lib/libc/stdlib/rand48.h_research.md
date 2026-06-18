# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/rand48.h

Internal header for the `drand48` family. It declares the shared 48-bit seed, multiplier, addend, and `__dorand48()` step function, plus the standard initial constants.

The header centralizes the LCG parameters used by `mrand48`, `nrand48`, `seed48`, `srand48`, and related files.
