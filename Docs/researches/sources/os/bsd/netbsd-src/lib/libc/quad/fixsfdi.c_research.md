# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixsfdi.c

Generic `float` to signed `quad_t` conversion via `__fixsfdi(float)`. It mirrors `fixdfdi.c`: clamp below `QUAD_MIN`, clamp above `QUAD_MAX`, and otherwise cast through `u_quad_t`, with special handling for negative values.

It is portable but depends on the compiler being able to perform the underlying floating-to-integer conversion.
