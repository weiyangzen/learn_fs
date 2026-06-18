# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/string/bzero.S

i386 `bzero` wrapper.

Key points:
- Defines `BZERO`.
- Includes `memset.S`, reusing the shared set implementation for zeroing.
