# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/Makefile.inc

Alpha libc architecture build fragment.

Key behavior:
- Adds `__longjmp14.c` and `__sigtramp2.S`.
- Generates division and remainder assembly files from `gen/divrem.m4` for signed/unsigned 32-bit and 64-bit operations.
- Adds generated files to `CLEANFILES`.
- Adds `CPPFLAGS+= -I.`.

Dependencies:
- NetBSD m4 tool and `arch/alpha/gen/divrem.m4`.
