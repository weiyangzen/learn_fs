# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/softfloat/or1k-gcc.h

This header adapts SoftFloat integer types and endian macros to or1k GCC. It derives `BIGENDIAN`/`LITTLEENDIAN` from `<machine/endian.h>`, enables `BITS64`, defines SoftFloat integer aliases and exact-width bit types, and supplies `LIT64` and `INLINE`.

It defines float64 mangle/demangle macros as identity operations. This file is architecture configuration rather than runtime logic.
