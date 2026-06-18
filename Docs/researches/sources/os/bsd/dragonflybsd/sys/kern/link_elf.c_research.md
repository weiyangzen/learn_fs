# File Research: sources/os/bsd/dragonflybsd/sys/kern/link_elf.c

Implements ELF kernel linker support for executable/dynamic-style KLD images and preloaded ELF modules.

Key data structures:
- `struct elf_file`: base relocation address, dynamic section pointers, SysV hash metadata, string/symbol tables, relocation tables, PLT relocation tables, preload module pointer, and debugger symbol/string tables.

Key registration:
- `link_elf_init()` registers `elf32` or `elf64` linker class, creates the kernel linker file from `_DYNAMIC`, parses dynamic metadata, processes preload symbol metadata, and marks the kernel linked.
- SYSINIT runs at `SI_BOOT2_KLD`.

Load paths:
- `link_elf_preload_file()` locates preloaded modules by name, validates type `"elf<N> module"` or `"elf module"`, obtains address/size/dynamic metadata, creates a linker file, parses dynamic metadata, and performs local relocations.
- `link_elf_preload_finish()` performs external relocations and parses module symbols.
- `link_elf_load_file()` searches linker path, opens the vnode with `nlookup`/`vn_open`, reads the first page, validates ELF identity/class/data/version/type/machine, expects two `PT_LOAD` segments and one `PT_DYNAMIC`, allocates kernel memory, reads text/data segments with `vn_rdwr()`, zeroes BSS, parses dynamic metadata, handles dependencies, performs relocations, and optionally loads section symbol/string tables for debugging.

Relocation and symbol behavior:
- `parse_dynamic()` processes `DT_HASH`, string/symbol tables, GOT, REL/RELA, JMPREL, PLT sizes, and PLT relocation type.
- `relocate_file()` runs `elf_reloc()` over REL, RELA, PLT REL, and PLT RELA entries, resolving via `elf_lookup()`.
- `link_elf_reloc_local()` performs local relocations first using `elf_reloc_local()`.
- `link_elf_lookup_symbol()` uses the SysV hash table first, then falls back to full debugger symbol table if present.
- `link_elf_symbol_values()` returns name, relocated value, and size.
- `link_elf_search_symbol()` finds nearest symbol at or below a given address.
- `link_elf_lookup_set()` resolves linker sets using `__start_set_<name>` and `__stop_set_<name>` symbols.
- `elf_hash()` implements the System V ABI hash algorithm.
- `elf_lookup()` resolves local symbols directly and otherwise delegates to `linker_file_lookup_symbol()`.

Unload behavior:
- `link_elf_unload_file()` frees loaded image memory and optional symbol/string bases.
- `link_elf_unload_module()` frees preload-private state and deletes preload metadata by pathname.

Filesystem relevance:
- Directly uses VFS/vnode operations to load kernel modules from the filesystem.
- Important for filesystem modules: this is one path by which filesystem KLDs can be loaded, linked, relocated, and have linker sets discovered.
