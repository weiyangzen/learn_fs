# File Research: sources/teaching/xv6-public/elf.h

Defines the ELF structures and constants used by the boot loader and `exec`.

Contents:
- `ELF_MAGIC`.
- `struct elfhdr` with ELF header metadata.
- `struct proghdr` with loadable segment metadata.
- Program header type `ELF_PROG_LOAD`.
- Segment flag bits for exec/write/read.

Important interactions:
- `bootmain.c` uses physical addresses from program headers.
- `exec.c` validates and loads user executable segments.
