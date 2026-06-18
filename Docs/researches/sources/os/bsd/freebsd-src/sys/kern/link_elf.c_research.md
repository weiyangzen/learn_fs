# File Research: sources/os/bsd/freebsd-src/sys/kern/link_elf.c

## Purpose
Implements FreeBSD's ELF executable/shared-object style kernel linker class (`elf32` or `elf64`) for preloaded and dynamically loaded kernel modules. It parses ELF dynamic sections, maps load segments, applies relocations, exposes symbols/debug/CTF data, manages linker sets, and integrates modules with GDB, DDB, per-CPU data, VNET data, and machine-dependent ELF hooks.

## Key Elements
- `struct elf_file` extends `struct linker_file` with ELF dynamic metadata, SysV hash tables, relocation tables, symbol/string tables, CTF data, constructor state, per-CPU/VNET relocation bases, and optional GDB link-map state.
- `link_elf_methods[]` implements the `linker_if.m` interface for symbol lookup, debug lookup, CTF, loading, unloading, preload finishing, linker sets, and function enumeration.
- `link_elf_init()` creates the kernel linker file from `_DYNAMIC` and preload metadata, parses kernel symbols, initializes linker set tracking, and invokes kernel constructors.
- `parse_dynamic()` handles `DT_HASH`, `DT_STRTAB`, `DT_SYMTAB`, `DT_REL*`, `DT_RELA*`, `DT_JMPREL`, `DT_PLTGOT`, `DT_PLTREL`, and GDB `DT_DEBUG`.
- `link_elf_link_preload()` and `link_elf_link_preload_finish()` attach to loader-preloaded KLDs, parse dynamic metadata, prepare pcpu/VNET storage, protect mappings, relocate, and finish MD registration.
- `link_elf_load_file()` opens a vnode, validates ELF headers, maps `PT_LOAD` segments, reads text/data, zeroes BSS, loads dependencies, relocates, applies final protections, and imports section symbol tables when present.

## Relocation and Symbol Resolution
- `relocate_file()` runs normal relocations first, then GNU IFUNC relocations.
- `relocate_file1()` iterates `REL`, `RELA`, PLT `REL`, and PLT `RELA` tables and calls MD `elf_reloc()`.
- `elf_lookup()` resolves local symbols directly by index and global/weak symbols through `linker_file_lookup_symbol()`.
- `elf_relocaddr()` rewrites addresses that fall in pcpu or VNET linker sets to their allocated runtime bases.
- `link_elf_reloc_local()` applies local relocations before dependencies and external resolution.

## Loader Memory Model
For file-backed loads, the code reserves one contiguous kernel mapping covering the ELF load address range. With `SPARSE_MAPPING`, it allocates a VM object, wires segment ranges, and later downgrades permissions by segment flags. Without it, it uses executable malloc memory. Preloaded modules use `pmap_change_prot()` on supported architectures to temporarily make text/data relocatable and then restore protections.

## Linker Sets, PCPU, and VNET
- `parse_dpcpu()` locates the `pcpu` linker set, validates i386 padding when relevant, allocates per-CPU storage with `dpcpu_alloc()`, copies initial data, and records an address translation range.
- `parse_vnet()` performs analogous setup for VNET data when `VIMAGE` is enabled.
- `elf_set_add()`, `elf_set_find()`, and `elf_set_delete()` maintain sorted non-overlapping address ranges for pcpu/VNET translation during relocation.
- `link_elf_lookup_set()` resolves `__start_set_<name>` and `__stop_set_<name>` symbols.

## Debug and Introspection
- DDB/debug symbols come from dynamic symbols or loader-provided symbol blocks for preloaded modules.
- `link_elf_lookup_debug_symbol()`, `link_elf_debug_symbol_values()`, `link_elf_search_symbol()`, and function iteration helpers support kernel debugging and tracing.
- CTF operations are supplied by included `kern/kern_ctf.c`.
- Optional GDB support maintains `r_debug` and a `link_map` list so a debugger can track module load/unload events.

## Filesystem / VM Relevance
Dynamic module loading is vnode-backed through `vn_open()`, `vn_rdwr()`, `VOP_UNLOCK()`, and `vn_close()`, with MAC load checks via `mac_kld_check_load()`. The loader directly manages kernel VM mappings, page protections, wiring, and executable memory, making it relevant to VM safety and executable code lifecycle.

## Notable Edge Cases
- Program headers are expected to fit in the first page; otherwise the code reports unreadable headers.
- `PT_INTERP` is rejected and dynamically linked objects without `PT_DYNAMIC` are rejected.
- Local symbol leakage into global resolution is tunable through `debug.link_elf_leak_locals`.
- IFUNC relocation is split into early and late paths, including `link_elf_ireloc()` and `link_elf_late_ireloc()` on supported architectures.
- Unload releases pcpu/VNET allocations, GDB link-map entries, mapped memory, symbol strings, and CTF buffers.
