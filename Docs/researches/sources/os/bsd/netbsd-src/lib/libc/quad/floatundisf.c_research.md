# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/floatundisf.c

Generic unsigned `u_quad_t` to `float` conversion. It uses the same high-word times `2^32` plus low-word pattern as the double variant, with double arithmetic used before returning a float.

This is simple and portable, relying on normal compiler floating conversion behavior.
