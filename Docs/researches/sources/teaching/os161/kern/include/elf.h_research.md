# File Research: sources/teaching/os161/kern/include/elf.h

Defines simplified 32-bit ELF structures and constants for OS/161 executable loading.

Key contents:
- `Elf32_Ehdr` and `Elf32_Phdr`.
- ELF identification constants, file classes, endianness encodings, OS ABI values.
- File types and machine IDs.
- Program header types and flags.
- Aliases `Elf_Ehdr` and `Elf_Phdr`.

Relevance:
- `load_elf` consumes files via vnode I/O and uses these structures to map executable segments into an address space.
