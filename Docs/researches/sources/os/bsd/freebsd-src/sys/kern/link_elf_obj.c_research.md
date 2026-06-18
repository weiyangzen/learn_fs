# File Research: sources/os/bsd/freebsd-src/sys/kern/link_elf_obj.c

## Purpose
Implements FreeBSD's ELF relocatable-object kernel linker class (`elf32_obj` or `elf64_obj`). Unlike `link_elf.c`, this loader is section-header driven for `ET_REL` modules: it loads allocated sections, builds section-to-runtime-address tables, applies local and external relocations, manages constructors/destructors, and exposes debug/CTF symbols.

## Key Elements
- `Elf_progent` records loaded program sections: runtime address, original address for debuggers, size, flags, original section number, and section name.
- `Elf_relent` and `Elf_relaent` record relocation tables and target section indexes.
- `struct elf_file` stores section headers, program/relocation tables, debug symbols, section string table, CTF data, VM object, and preload state.
- `link_elf_methods[]` implements the same linker interface as `link_elf.c`, but with object-file lookup semantics.
- `link_elf_init()` registers the object linker class at `SI_SUB_KLD`.

## Loading Paths
`link_elf_link_preload()` handles loader-preloaded `ET_REL` modules whose ELF header, section headers, and section contents were already placed in memory. It validates target class/data/machine, relocates saved `sh_addr` values relative to the preload base, builds program and relocation tables, allocates pcpu/VNET section storage, fixes constructor/destructor addresses, and applies local relocations.

`link_elf_load_file()` opens a vnode, reads the ELF header and section headers, validates that exactly one symbol table exists, reads symbol/string/section-name tables, computes a contiguous kernel mapping size for allocated sections, maps and wires a VM object, reads `PROGBITS` and unwind sections, zeroes `NOBITS`, loads relocation tables, updates symbol values to runtime addresses, loads dependencies, performs external relocations, calls MD load hooks, resolves IFUNCs, protects the mapping, invokes constructors, and returns the linker file.

## Relocation and Symbol Resolution
- `link_elf_reloc_local()` handles local relocations and fixes `__start_`/`__stop_` linker-set symbols before relocation.
- `relocate_file()` applies external relocations, again in normal then IFUNC phases.
- `elf_obj_lookup()` resolves defined symbols from adjusted `st_value`, calls IFUNC resolvers when needed, and resolves undefined globals/weak symbols through `linker_file_lookup_symbol()`.
- Successful global lookup results are temporarily cached with `SHN_FREEBSD_CACHED` and later cleaned by `elf_obj_cleanup_globals_cache()`.
- `findbase()` maps a relocation target section number to its loaded section base.

## Memory Protection and Lifecycle
The loader initially grants write/execute access while relocations run, then `link_elf_protect()` derives final page protections from section flags. Since sections can share pages, it merges protections for overlapping page ranges and protects gaps as read-only or read-write for preloaded trailing data. `link_elf_unload_file()` invokes destructors, calls MD unload hooks, frees pcpu/VNET allocations, resets preload mapping protections, removes VM mappings, and frees symbols, relocation tables, section names, and CTF buffers.

## Linker Sets, PCPU, and VNET
- Linker sets are represented as sections named `set_<name>` and returned directly by `link_elf_lookup_set()`.
- `DPCPU_SETNAME` sections are copied into `dpcpu_alloc()` storage and initialized with `dpcpu_copy()`.
- With `VIMAGE`, `VNET_SETNAME` sections are copied into `vnet_data_alloc()` storage and initialized/saved through VNET helpers.
- `link_elf_propagate_vnets()` copies stored VNET data into all VNET instances.

## Filesystem / VM Relevance
This file combines vnode I/O (`vn_open()`, `vn_rdwr()`, `vn_close()`), MAC KLD authorization, kernel VM object allocation, wired mappings, page protections, and executable code loading. It is important for understanding how FreeBSD turns filesystem-resident KLD object files into live kernel text/data.

## Notable Edge Cases
- Non-allocated sections and relocation tables for non-allocated sections are ignored.
- Files with no allocated contents, invalid string tables, or anything other than exactly one symbol table are rejected.
- Constructor sections may be old `.ctors` or `SHT_INIT_ARRAY`; destructor sections may be `.dtors` or `SHT_FINI_ARRAY`.
- `debug.link_elf_obj_leak_locals` controls whether local symbols can participate in global module symbol resolution.
- On i386/amd64, IFUNC local relocations are performed after MD module load notification.
