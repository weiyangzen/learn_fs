# File Research: sources/os/bsd/dragonflybsd/sys/kern/link_elf_obj.c

Implements ELF relocatable-object kernel linker support for ET_REL KLD object modules.

Key data structures:
- `Elf_progent`: loaded program/NOBITS section address, size, flags, original section index, section name.
- `Elf_relent` and `Elf_relaent`: relocation table pointer/count/target section.
- `struct elf_file`: preload flag, mapped address/size, VM object, section headers, progtab, REL/RELA tables, debugger symbol/string tables, section string table, and optional CTF-related storage.

Key registration:
- `link_elf_obj_init()` registers `elf32` or `elf64` linker class with object-module loader hooks.
- SYSINIT runs at `SI_BOOT2_KLD`.

Preload path:
- `link_elf_obj_preload_file()` locates a preloaded `"elf<N> obj module"` or `"elf obj module"`, validates ET_REL header metadata, uses preloaded section headers, counts PROGBITS/NOBITS/SYMTAB/REL/RELA sections, builds tracking tables, relocates saved section addresses to runtime address, binds symbols to loaded section addresses, records relocation tables, performs local relocations, and returns the linker file.
- `link_elf_obj_preload_finish()` performs external relocations.

Filesystem load path:
- `link_elf_obj_load_file()` searches linker path, opens a vnode with `nlookup`/`vn_open`, reads ELF header, validates class/data/version/type/machine, reads section headers, validates one symbol table and associated string table, loads symbol and string tables, optionally loads section name strings, sizes all PROGBITS/NOBITS sections with alignment, allocates a VM object and kernel mapping, wires pages, loads PROGBITS from vnode with `vn_rdwr()`, zeroes NOBITS, loads REL/RELA sections, adjusts symbol values to loaded addresses, performs local relocations, loads dependencies, then performs external relocations.

Relocation and symbol behavior:
- `findbase()` maps a relocation section’s target section index to its loaded base address.
- `relocate_file()` processes all REL/RELA entries except local symbols, calling `elf_reloc()` with `elf_obj_lookup()`.
- `link_elf_obj_reloc_local()` first fixes linker-set start/stop symbols, then applies only local REL/RELA relocations using `elf_reloc_local()`.
- `elf_obj_lookup()` resolves defined symbols directly from adjusted `st_value`; undefined globals are delegated to `linker_file_lookup_symbol()`. Undefined locals and weak symbols fail.
- `link_elf_obj_lookup_symbol()` linearly searches the symbol table for defined symbols by name.
- `link_elf_obj_symbol_values()` returns symbol name, absolute value, and size.
- `link_elf_obj_search_symbol()` finds nearest symbol for address lookup.
- `link_elf_obj_lookup_set()` finds sections named `set_<name>` and returns start/stop/count.
- `link_elf_obj_fix_link_set()` resolves undefined `__start_<section>` and `__stop_<section>` symbols to matching loaded section bounds.

Unload behavior:
- `link_elf_obj_unload_file()` frees relocation tables, progtab, CTF storage, loaded VM mapping/object, section headers, symbols, string tables, and preload metadata. Preloaded modules do not reclaim module memory here.

Filesystem relevance:
- Directly loads ET_REL kernel modules from the filesystem through vnode reads.
- Critical for filesystem drivers built as relocatable KLDs: it allocates executable kernel memory, resolves dependencies, applies relocations, and exposes linker sets used by module registration machinery.
