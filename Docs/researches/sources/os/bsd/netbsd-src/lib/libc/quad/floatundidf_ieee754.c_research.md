# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatundidf_ieee754.c

IEEE-754-specific unsigned `u_quad_t` to `double` conversion. It returns zero for zero, normalizes the integer with `__builtin_clzll()`, fills double fraction fields, and sets the biased exponent.

This constructs the destination double directly rather than using floating arithmetic.
