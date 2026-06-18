# File Research: sources/os/bsd/netbsd-src/lib/libarch/x86_64/Makefile.inc

Build fragment for x86_64 libarch wrappers.

Key behavior:
- Adds `x86_64_mtrr.c` and `x86_64_iopl.c` for native x86_64 builds, excluding the i386 multilib directory.
- Installs manpages for `x86_64_get_mtrr` and `x86_64_iopl`.
- Adds a manpage link from `x86_64_get_mtrr.2` to `x86_64_set_mtrr.2`.

Dependencies:
- `${MACHINE_ARCH}` and `${MLIBDIR}`.
