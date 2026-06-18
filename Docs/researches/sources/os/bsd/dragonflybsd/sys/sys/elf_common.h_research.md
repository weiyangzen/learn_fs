# File Research: sources/os/bsd/dragonflybsd/sys/sys/elf_common.h

`elf_common.h` contains ELF definitions independent of word size and architecture. It defines `Elf_Note`, identification indexes, magic constants, ELF class/data/OSABI values, `IS_ELF()`, object types, machine IDs, special section indexes, program header types, segment permission flags, section types, section flags, note types, symbol bindings/types/visibility values, dynamic tags, dynamic flags, versioning constants, syminfo constants, and section group flags.

This is the shared vocabulary for `elf32.h`, `elf64.h`, `imgact_elf.h`, loaders, debuggers, coredump handling, and binary utilities. Much of the file mirrors generic ELF, GNU, Solaris, and platform extension registries.

The file is table-like and ABI-sensitive: changing numeric constants or aliases would affect binary compatibility and ELF parsing.
