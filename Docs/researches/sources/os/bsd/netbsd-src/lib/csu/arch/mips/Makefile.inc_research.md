# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/mips/Makefile.inc

MIPS CSU make include. It adds the architecture include directory and defines `ELFSIZE=_MIPS_SZPTR`.

This lets the same sources adapt to the active MIPS pointer width.
