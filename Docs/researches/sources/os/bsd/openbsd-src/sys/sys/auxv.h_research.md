# File Research: sources/os/bsd/openbsd-src/sys/sys/auxv.h

Purpose: Defines auxiliary vector constants and the user API for retrieving aux entries.

Key contents:
- Includes system types and machine ELF definitions.
- Defines `AT_NULL`, `AT_IGNORE`, `AT_PAGESZ`, `AT_HWCAP`, `AT_HWCAP2`, and `AT_COUNT`.
- Declares `elf_aux_info(int aux, void *buf, int buflen)`.

Filesystem relevance:
- Not directly filesystem code, but ELF execution paths that load binaries from VFS populate auxiliary vectors.
