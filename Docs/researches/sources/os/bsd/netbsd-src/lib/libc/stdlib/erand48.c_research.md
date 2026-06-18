# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/erand48.c

Read completely: 42 lines.

Generic `erand48()` implementation. It advances the caller-provided three-word seed with `__dorand48()` and builds a double in `[0, 1)` using three `ldexp()` terms for the low, middle, and high 16-bit seed words.

This version is portable and representation-independent.
