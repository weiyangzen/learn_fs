# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/qdiv.c

Implements `qdiv(quad_t num, quad_t denom)` returning `qdiv_t` quotient and remainder. It computes C division and modulus, then adjusts the quotient/remainder pair for the historical `div.c` convention when `num >= 0` but the remainder is negative.

Division-by-zero behavior is not handled here and follows the underlying C operation.
