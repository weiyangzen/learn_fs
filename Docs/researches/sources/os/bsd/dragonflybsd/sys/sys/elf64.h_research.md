# File Research: sources/os/bsd/dragonflybsd/sys/sys/elf64.h

`elf64.h` defines the 64-bit class-dependent ELF ABI. It includes `sys/types.h` and `sys/elf_common.h`.

It declares 64-bit `Elf64_*` scalar types, 64-bit ELF/section/program/dynamic/relocation/symbol/versioning structures, `Elf64_Nhdr`, move and hardware/software capability entries, and syminfo records. It also defines relocation, move, symbol, and visibility macros.

Compared with `elf32.h`, this header carries 64-bit-specific relocation type-data helpers and capability/move records. It is the 64-bit counterpart used by kernel ELF image activation, coredumps, and format-aware tooling.
