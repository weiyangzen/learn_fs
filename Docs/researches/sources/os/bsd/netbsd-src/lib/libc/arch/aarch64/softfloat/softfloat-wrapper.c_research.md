# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/softfloat-wrapper.c

Single-line wrapper source.

Key behavior:
- Includes `<softfloat.c>` so the common SoftFloat implementation is compiled through an architecture-local source file.

Dependencies:
- Include paths set by `arch/aarch64/Makefile.inc`.
