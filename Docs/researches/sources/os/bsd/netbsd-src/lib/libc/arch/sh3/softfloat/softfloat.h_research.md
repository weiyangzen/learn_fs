# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/softfloat/softfloat.h

## Summary
Declares the SH3 SoftFloat public API for software IEEE floating-point operations.

## Key Details
- Defines `float32` and `float64` storage types.
- Leaves `FLOATX80` and `FLOAT128` disabled by default.
- Exposes rounding mode and exception state through NetBSD `<machine/ieeefp.h>` types.
- Declares conversions among integer, single, and double precision formats.
- Optionally declares extended and quadruple precision APIs if their feature macros are enabled.
- Omits selected libgcc-provided 64-bit conversion declarations under `SOFTFLOAT_FOR_GCC`.

## Notes
This header is a declaration layer only; it depends on matching SoftFloat implementation files and `milieu.h` typedefs.
