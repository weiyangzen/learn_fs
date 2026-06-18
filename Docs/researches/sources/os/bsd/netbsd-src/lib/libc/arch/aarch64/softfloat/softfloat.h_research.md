# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/softfloat.h

AArch64-adapted SoftFloat API header.

Key behavior:
- Enables `FLOAT128` and leaves `FLOATX80` disabled.
- Includes `softfloat-qp.h`, `<sys/endian.h>`, and `<machine/ieeefp.h>`.
- Defines SoftFloat storage types `float32`, `float64`, and endian-aware `float128`.
- Declares rounding mode and exception flag globals using NetBSD `fp_rnd` and `fp_except`.
- Maps SoftFloat rounding and exception constants to NetBSD floating-point constants.
- Declares integer/float conversion routines, arithmetic routines, comparisons, rounding, remainder, sqrt, and NaN predicates for float32, float64, and float128.
- Contains conditional declarations for disabled floatx80 support.

Dependencies:
- SoftFloat Release 2a conventions.
- NetBSD IEEE floating-point exception and rounding definitions.
