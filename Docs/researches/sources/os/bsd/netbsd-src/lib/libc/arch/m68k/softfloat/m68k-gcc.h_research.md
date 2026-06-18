# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/softfloat/m68k-gcc.h

This header adapts John Hauser SoftFloat types to NetBSD/m68k GCC. It derives `BIGENDIAN` or `LITTLEENDIAN` from `<machine/endian.h>`, enables `BITS64`, defines SoftFloat integer aliases such as `flag`, `bits32`, `bits64`, and supplies `LIT64` and `INLINE`.

It also defines `FLOAT64_DEMANGLE` and `FLOAT64_MANGLE` as identity macros for this port. The header is a low-level ABI contract for all m68k softfloat sources; type width changes would cascade into every declared SoftFloat operation.
