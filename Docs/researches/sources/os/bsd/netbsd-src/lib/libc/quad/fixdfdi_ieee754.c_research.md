# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixdfdi_ieee754.c

IEEE-754-specific `double` to signed `quad_t` conversion. It unpacks `union ieee_double_u`, derives exponent and sign, builds the integer from the implicit bit plus high/low fraction fields, shifts according to exponent, and applies sign.

Out-of-range exponents clamp to `QUAD_MIN` or `QUAD_MAX`. Unlike the generic version, this avoids relying on compiler/runtime double-to-64-bit casts, which is important on architectures needing these helpers to implement those casts.
