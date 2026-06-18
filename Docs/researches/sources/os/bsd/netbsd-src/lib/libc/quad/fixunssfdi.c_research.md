# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixunssfdi.c

Generic `float` to unsigned `u_quad_t` conversion. It promotes the float to double for arithmetic, maps negative and out-of-range values to `UQUAD_MAX`, estimates the high 32-bit part, then adjusts for rounding drift before assigning the low word.

This implementation is defensive around floating rounding and old compiler behavior. It shares historical semantics with the other unsigned conversion helpers: negative does not become zero.
