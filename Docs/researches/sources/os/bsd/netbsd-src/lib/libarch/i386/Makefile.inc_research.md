# File Research: sources/os/bsd/netbsd-src/lib/libarch/i386/Makefile.inc

Build fragment for i386 libarch wrappers.

Key behavior:
- Adds LDT, IOPL, I/O permission, and MTRR wrapper sources when building native i386 or the i386 multilib directory.
- Installs manpages for `i386_get_ldt`, `i386_get_mtrr`, and `i386_iopl`.
- Adds manpage links for setter variants.

Dependencies:
- `${MACHINE_ARCH}` and `${MLIBDIR}` build variables.
