# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/string/bcopy.S

ARM `bcopy` wrapper.

Key points:
- Defines `_BCOPY`.
- Includes `memmove.S`, reusing the memmove implementation under bcopy semantics.
