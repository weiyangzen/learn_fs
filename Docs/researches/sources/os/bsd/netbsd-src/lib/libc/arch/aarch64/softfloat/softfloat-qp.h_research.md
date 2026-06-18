# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/softfloat-qp.h

Namespace-control header for AArch64 SoftFloat quad support.

Key behavior:
- When `SOFTFLOATAARCH64_FOR_GCC` is defined without `SOFTFLOAT_FOR_GCC`, renames common SoftFloat globals and float32/float64 helpers into `_softfloat_*` symbols.
- Always renames float128 functions under `SOFTFLOATAARCH64_FOR_GCC`.
- Defines `SOFTFLOAT_FOR_GCC` after the rename block if it was not already defined, reducing extraneous compiled SoftFloat code.

Dependencies:
- Inclusion before common `softfloat.c` via `softfloat.h`.

Notes:
- The file prevents SoftFloat implementation details from leaking into the public libc namespace.
