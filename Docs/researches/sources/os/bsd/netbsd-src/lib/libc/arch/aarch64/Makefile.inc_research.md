# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/Makefile.inc

AArch64 libc architecture build fragment.

Key behavior:
- Adds `__sigtramp2.S`.
- Adds architecture softfloat path and builds `qp.c`.
- Defines `SOFTFLOATAARCH64_FOR_GCC`, `EXCEPTIONS_WITH_SOFTFLOAT`, and `SOFTFLOAT_NEED_FIXUNS`.
- Builds `softfloat-wrapper.c` as the wrapper around common `softfloat.c`.
- Adds softfloat include paths for architecture and common bits64 headers.

Dependencies:
- AArch64 softfloat sources and common libc softfloat implementation.

Notes:
- Commented `qdivrem.c` indicates older or optional quad-precision support path is disabled.
