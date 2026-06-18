# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/softfloat.h

## Summary
Declares the SPARC64 SoftFloat API with quadruple precision enabled.

## Key Details
- Defines `FLOAT128`; leaves `FLOATX80` disabled.
- Includes `softfloat-qp.h` before `<machine/ieeefp.h>` for symbol remapping.
- Defines `float32`, `float64`, and `float128`.
- Declares rounding mode, exception flags, and `float_raise`.
- Declares conversions and operations for single, double, and quad precision.
- Includes unsigned conversion declarations needed by GCC/libc support.

## Notes
Compared with SH3, this header enables quad precision and exposes more conversion routines.
