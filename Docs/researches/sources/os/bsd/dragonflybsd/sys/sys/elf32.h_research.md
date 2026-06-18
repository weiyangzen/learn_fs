# File Research: sources/os/bsd/dragonflybsd/sys/sys/elf32.h

`elf32.h` defines the 32-bit class-dependent ELF ABI types and records. It includes `sys/types.h` and `sys/elf_common.h`.

It declares 32-bit `Elf32_*` scalar types, ELF header, section header, program header, dynamic entry, relocation records with and without addends, symbol entries, GNU/Sun versioning structures, version-symbol type, and symbol-info records.

The header also provides macros for packing/unpacking relocation `r_info`, symbol `st_info`, and symbol visibility. It is a pure format-definition header used by loaders, linkers, coredump code, and binary parsers.
