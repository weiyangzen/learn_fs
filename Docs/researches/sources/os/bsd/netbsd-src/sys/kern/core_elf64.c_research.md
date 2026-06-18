# File Research: sources/os/bsd/netbsd-src/sys/kern/core_elf64.c

## Purpose
Instantiates the ELF core dump implementation for 64-bit ELF.

## Main Interfaces
- Defines `ELFSIZE 64`.
- Includes `core_elf32.c`, causing the shared ELF core implementation to compile with 64-bit ELF types and symbol names.

## Implementation Notes
This is a template-inclusion wrapper rather than an independent implementation.

## Dependencies
Depends entirely on `core_elf32.c` and ELF macro indirection in the NetBSD exec headers.
