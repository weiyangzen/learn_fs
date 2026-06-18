# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/softfloat/sh3-gcc.h

## Summary
Defines SH3 GCC-specific SoftFloat integer and compiler settings.

## Key Details
- Maps `<machine/endian.h>` to `BIGENDIAN` or `LITTLEENDIAN`.
- Enables `BITS64`.
- Defines SoftFloat convenience integer types such as `flag`, `uint32`, `bits64`, and signed counterparts.
- Defines `LIT64(a)` as a `long long` literal suffix helper.
- Defines `INLINE` as `static inline`.
- Leaves `FLOAT64_DEMANGLE` and `FLOAT64_MANGLE` as identity macros.

## Notes
The typedefs are tuned for SH3/GCC assumptions rather than strict fixed-width standard typedefs.
