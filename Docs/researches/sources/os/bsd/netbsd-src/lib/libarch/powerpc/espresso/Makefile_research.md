# File Research: sources/os/bsd/netbsd-src/lib/libarch/powerpc/espresso/Makefile

Builds the `powerpc_espresso` shared support library.

Key behavior:
- Builds a no-profile, no-lint, no-linklib library installed in the shared library directory.
- Avoids libc with empty `DPLIBC` and `LDLIBC=-nodefaultlibs`.
- Adds assembler flags `-mcpu=750 -DPPC_IBMESPRESSO`.
- Uses atomic sources from `common/lib/libc/arch/powerpc/atomic/Makefile.inc`.

Dependencies:
- NetBSD common PowerPC atomic implementation.
- PowerPC 750/Espresso assembler support.

Notes:
- This library is intentionally self-contained and avoids libc dependencies.
