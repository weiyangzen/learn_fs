# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatundisf_ieee754.c

IEEE-754-specific unsigned `u_quad_t` to `float` conversion. It handles zero and one, computes the leading set bit, fills the single-precision fraction field, and sets the exponent.

The implementation has separate LP64 and 32-bit code paths, matching `floatdisf_ieee754.c` without sign handling.
