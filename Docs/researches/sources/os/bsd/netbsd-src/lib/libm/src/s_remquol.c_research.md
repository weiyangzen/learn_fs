# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_remquol.c

Implements long-double `remquol()` using extended significand word subtraction.

Key behavior: handles exceptional values via `nan_mix_op`, normalizes subnormal operands, computes remainder and quotient bits with high/low significand words, applies nearest-even fixup, and restores sign.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `math_private.h`, `fabsl`, `nan_mix_op`, and long-double field macros.

Notable risks: assumes high and low significand parts fit configured integer types and that explicit integer-bit macros match architecture.
