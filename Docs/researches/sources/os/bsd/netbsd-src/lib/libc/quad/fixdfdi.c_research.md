# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixdfdi.c

Implements `__fixdfdi(double)`, converting `double` to signed 64-bit `quad_t`. It clamps values below `QUAD_MIN` and above `QUAD_MAX`, and otherwise casts through `u_quad_t`, handling negative values by negating after unsigned conversion.

This is the generic conversion implementation used where direct floating conversion is acceptable. It includes softfloat glue for `SOFTFLOAT` or ARM EABI builds, then relies on `quad.h` constants.
