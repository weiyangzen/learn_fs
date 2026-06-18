# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/arm/Makefile.inc

ARM CSU make include. It adds the architecture include directory and conditionally defines `HAVE_INITFINI_ARRAY` when CPU flags select an AAPCS ABI.

It also emits `ELF_NOTE_MARCH_DESC` with `CSU_MACHINE_ARCH`, allowing ARM binaries to carry a machine-architecture ELF note.
