# File Research: sources/os/bsd/freebsd-src/sys/sys/elf64.h

## Purpose
Defines class-dependent ELF64 scalar types, structures, and field packing macros common to all 64-bit ELF architectures.

## Main Elements
- ELF64 scalar typedefs for addresses, offsets, words, extended words, sizes, signed sizes, and hash elements.
- Structures: ELF header, MIPS liblist, section header, program header, dynamic entry, relocations, RELR, note header, move entry, capabilities, symbol table, version definitions/needs, symbol info, and compressed section header.
- Macros pack/unpack relocation info, including type-data/type-id variants, move info, symbol binding/type, and symbol visibility.

## Dependencies And Integration
Includes `sys/elf_common.h`; used by ELF consumers across kernel and userland for 64-bit objects.

## Risk Notes
`Elf64_Hashelt` is noted as inconsistent among 64-bit architectures, so machine-dependent headers may override or refine expectations. Structure layout is ELF ABI-critical.
