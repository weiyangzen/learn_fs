# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/earm/Makefile.inc

EABI ARM CSU make include. It adds the architecture include directory, unconditionally defines `HAVE_INITFINI_ARRAY`, and emits an `ELF_NOTE_MARCH_DESC`.

This selects the array-based constructor/destructor path for `earm*` architectures.
