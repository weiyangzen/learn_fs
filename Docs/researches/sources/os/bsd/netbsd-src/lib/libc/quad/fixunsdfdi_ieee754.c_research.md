# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/fixunsdfdi_ieee754.c

IEEE-754-specific `double` to unsigned `u_quad_t` conversion. It unpacks sign, exponent, and fraction fields directly. Negative inputs and exponent values above 63 return `UQUAD_MAX`; negative exponents return zero.

The conversion assembles the implicit bit, high fraction, and low fraction into a 64-bit unsigned result with right or left shifts based on exponent.
