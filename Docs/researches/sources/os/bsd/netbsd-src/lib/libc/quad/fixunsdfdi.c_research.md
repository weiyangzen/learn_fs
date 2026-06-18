# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixunsdfdi.c

Generic `double` to unsigned `u_quad_t` conversion via `__fixunsdfdi(double)`. Negative inputs return `UQUAD_MAX` per this historical helper’s semantics. Inputs at or above `2^64 - 1` also return `UQUAD_MAX`.

For in-range values, it divides by `2^32` to form the high word and subtracts to form the low word in a `union uu`. Comments call out old GCC issues and rounding assumptions.
