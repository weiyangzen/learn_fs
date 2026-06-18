# File Research: sources/os/bsd/freebsd-src/sys/sys/elf32.h

## Purpose
Defines class-dependent ELF32 scalar types, structures, and field packing macros common to all 32-bit ELF architectures.

## Main Elements
- ELF32 scalar typedefs for addresses, offsets, words, signed words, sizes, and hash elements.
- Structures: ELF header, MIPS liblist, section header, program header, dynamic entry, relocations, RELR, note header, move entry, capabilities, symbol table, version definitions/needs, symbol info, and compressed section header.
- Macros pack/unpack relocation info, move info, symbol binding/type, and symbol visibility.

## Dependencies And Integration
Includes `sys/elf_common.h`; used by loaders, linkers, kernel module code, debuggers, and ELF parsers.

## Risk Notes
Structure layouts mirror the ELF specification. Architecture-specific relocation IDs and machine flags are defined elsewhere.
