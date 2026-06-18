# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/byteorder.h

This header provides i386 byte-swap helpers adapted from Linux-style headers.

Core contents:
- Includes `compiler.h`.
- Under GCC, defines inline assembly implementations for 32-bit and 64-bit byte swaps.
- Exposes `__arch__swab32`, `__arch__swab64`, and `__BYTEORDER_HAS_U64__`.

Risk points:
- The inline assembly is x86/GCC-specific.
- The little-endian include is commented out, so actual endian conversion macros must come from elsewhere.
- This is portability support for vendored code, not ReactOS-specific logic.
