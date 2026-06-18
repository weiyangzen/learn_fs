# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/elf.h

Purpose: local ELF constants and prototypes shared by linker ELF emitters.

Key behavior: defines ELF header sizes, identity/type/machine/program-header/section-header constants, permissions, `Putl`, and prototypes for `elf32`, `elf64`, and header-writing helpers.

Integration notes: included by `l.h`; constants are copied from Plan 9 libmach and used directly by `asm.c` and `elf.c`.
