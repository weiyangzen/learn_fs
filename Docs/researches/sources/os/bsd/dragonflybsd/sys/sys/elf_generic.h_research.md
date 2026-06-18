# File Research: sources/os/bsd/dragonflybsd/sys/sys/elf_generic.h

`elf_generic.h` maps generic `Elf_*`, `ELF_*`, and helper names to either 32-bit or 64-bit ELF definitions based on `__ELF_WORD_SIZE`.

It validates that `__ELF_WORD_SIZE` is 32 or 64, derives `ELF_CLASS` and `ELF_DATA` from machine byte order, defines concatenation helpers such as `__ElfN()`, and provides Linux-compatible `ElfW(x)`. It typedefs common generic names and maps generic relocation/symbol macros to the selected class.

The header must be included after the relevant machine/ELF setup. If `__ELF_WORD_SIZE` is absent, it emits a warning rather than providing generic names.
