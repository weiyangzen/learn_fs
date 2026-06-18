# File Research: sources/os/bsd/freebsd-src/sys/sys/elf_generic.h

## Purpose
Provides generic ELF type and macro aliases that resolve to either 32-bit or 64-bit ELF definitions based on `__ELF_WORD_SIZE`.

## Main Interfaces
- Requires `__ELF_WORD_SIZE` to be exactly `32` or `64`.
- Defines `ELF_CLASS` and `ELF_DATA` from word size and `BYTE_ORDER`.
- Name construction macros: `__elfN`, `__ElfN`, `__ELFN`, `__ElfType`.
- Linux-compatible `ElfW(x)` alias.
- Generic typedefs: `Elf_Addr`, `Elf_Ehdr`, `Elf_Shdr`, `Elf_Phdr`, `Elf_Dyn`, `Elf_Rel`, `Elf_Rela`, `Elf_Relr`, `Elf_Sym`, versioning types, and non-standard hash/size types.
- Generic relocation and symbol helper aliases: `ELF_R_SYM`, `ELF_R_TYPE`, `ELF_R_INFO`, `ELF_ST_*`.

## Dependencies And Integration
Depends on `sys/cdefs.h`, byte-order macros, and the word-size-specific ELF types having been defined by the including ELF header path. It is a convenience layer for code that should not spell `Elf32_*` or `Elf64_*`.

## Risk Notes
Incorrect `__ELF_WORD_SIZE` or missing byte-order definitions fail at preprocessing time. Changes here can break broad ELF consumers because it controls canonical generic type names.
