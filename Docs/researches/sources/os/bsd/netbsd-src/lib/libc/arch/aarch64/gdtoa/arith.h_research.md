# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/gdtoa/arith.h

AArch64 gdtoa endian configuration.

Key behavior:
- Defines `IEEE_BIG_ENDIAN` when `__AARCH64EB__` is set.
- Otherwise defines `IEEE_LITTLE_ENDIAN`.

Dependencies:
- Compiler target endian macro `__AARCH64EB__`.
