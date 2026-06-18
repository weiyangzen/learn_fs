# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatdisf.c

Generic signed `quad_t` to `float` conversion via `__floatdisf()`. It splits the magnitude into high/low words, computes the value using double arithmetic, assigns to float, and reapplies sign.

The code comments note that using double is conservative. It is portable and representation-agnostic.
