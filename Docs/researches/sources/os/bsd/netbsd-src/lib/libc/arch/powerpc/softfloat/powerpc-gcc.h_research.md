# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/softfloat/powerpc-gcc.h

This header maps SoftFloat’s integer and endian configuration to PowerPC GCC. It derives endian macros from `<machine/endian.h>`, enables 64-bit integer support, defines SoftFloat convenience and exact-width integer types, and supplies `LIT64` and `INLINE`.

It defines float64 mangle/demangle as identity operations. The file contains no runtime code but is foundational for softfloat type consistency.
