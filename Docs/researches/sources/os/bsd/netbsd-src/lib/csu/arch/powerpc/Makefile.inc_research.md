# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/Makefile.inc

PowerPC CSU make include. It adds the architecture include directory.

No ELF size is hard-coded here; the assembly uses `_LP64`, `SZREG`, and related machine macros.
