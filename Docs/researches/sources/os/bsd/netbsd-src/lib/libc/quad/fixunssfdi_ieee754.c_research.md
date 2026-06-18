# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixunssfdi_ieee754.c

IEEE-754-specific `float` to unsigned `u_quad_t` conversion. It unpacks `union ieee_single_u`, returns `UQUAD_MAX` for negative or exponent-above-63 values, returns zero for exponent below zero, and otherwise shifts the implicit bit plus single-precision fraction.

This is the ARM/IEEE path avoiding dependency on compiler-emitted cast helpers.
