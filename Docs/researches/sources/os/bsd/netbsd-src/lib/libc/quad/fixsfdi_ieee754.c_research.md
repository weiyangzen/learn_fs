# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixsfdi_ieee754.c

IEEE-754-specific `float` to signed `quad_t` conversion. It unpacks `union ieee_single_u`, handles negative/positive sign, returns zero for exponent below zero, clamps exponent above 62, and shifts the implicit-bit-plus-fraction integer into place.

This provides a cast implementation that does not recursively depend on compiler-provided 64-bit conversion support.
