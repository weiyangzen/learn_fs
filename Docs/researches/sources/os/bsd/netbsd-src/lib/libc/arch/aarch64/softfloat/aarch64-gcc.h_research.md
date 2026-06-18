# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/aarch64-gcc.h

SoftFloat compiler/environment configuration for AArch64.

Key behavior:
- Includes `<machine/endian.h>` and defines `BIGENDIAN` or `LITTLEENDIAN`.
- Defines `BITS64`.
- Defines SoftFloat integer typedefs such as `flag`, `uint8`, `int8`, `uint32`, `int32`, `uint64`, and exact-width `bits*`/`sbits*` types.
- Defines `LIT64(a)` as `a##LL`.
- Defines `INLINE` as `static inline`.
- Defines `FLOAT64_DEMANGLE` and `FLOAT64_MANGLE` as identity macros.

Dependencies:
- NetBSD machine endian definitions.
