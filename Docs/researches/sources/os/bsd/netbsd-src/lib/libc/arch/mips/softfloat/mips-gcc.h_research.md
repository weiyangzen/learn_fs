# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/softfloat/mips-gcc.h

This header adapts SoftFloat’s integer and endian assumptions for MIPS GCC. It chooses `BIGENDIAN` via `__MIPSEB__` and `LITTLEENDIAN` otherwise, enables `BITS64`, defines SoftFloat integer aliases and exact-width bit types, and supplies `LIT64` plus `INLINE`.

It documents MIPS floating-point word-order oddities and defines identity `FLOAT64_DEMANGLE` / `FLOAT64_MANGLE` only under `SOFTFLOAT_FOR_GCC`. This conditional matters for compiler-helper builds versus libc softfloat builds.
