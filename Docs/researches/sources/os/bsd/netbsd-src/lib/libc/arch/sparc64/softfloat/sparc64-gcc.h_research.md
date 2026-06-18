# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sparc64/softfloat/sparc64-gcc.h

## Summary
Defines SPARC64 GCC-specific SoftFloat portability types.

## Key Details
- Maps machine byte order to `BIGENDIAN` or `LITTLEENDIAN`.
- Enables `BITS64`.
- Defines SoftFloat convenience and exact-width integer typedefs.
- Defines `LIT64(a)` as a `long long` literal helper.
- Defines `INLINE` as `static inline`.
- Leaves float64 mangle/demangle macros as identity transforms.

## Notes
The `uint8` and `int8` convenience typedefs are `int`, matching SoftFloat's portability model.
