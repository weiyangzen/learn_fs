# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_truncl.c

Implements `truncl()` for extended long double using `union ieee_ext_u`. It computes the exponent position, clears fractional bits in high or low fraction words, and returns signed zero for `|x| < 1`.

Important dependencies: `namespace.h`, `<float.h>`, `<math.h>`, `<stdint.h>`, `<machine/ieee.h>`, `LDBL_IMPLICIT_NBIT`, and long-double fraction layout macros.

The implementation exists only under `__HAVE_LONG_DOUBLE`; it preserves floating-point exception behavior with the same large-constant inexact trigger pattern.
