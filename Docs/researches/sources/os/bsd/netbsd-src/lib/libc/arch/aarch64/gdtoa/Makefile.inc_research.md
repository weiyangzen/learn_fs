# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/gdtoa/Makefile.inc

AArch64 gdtoa build fragment.

Key behavior:
- Adds `strtof.c`, `strtold_pQ.c`, and `strtopQ.c`.

Dependencies:
- Common gdtoa sources configured for AArch64 quad/long-double layout.
