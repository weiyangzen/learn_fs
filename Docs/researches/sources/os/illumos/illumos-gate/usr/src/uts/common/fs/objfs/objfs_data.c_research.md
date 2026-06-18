# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_data.c

## Purpose
Implements `/system/object/<module>/object`, a synthetic read-only ELF file exposing metadata about a loaded kernel module for consumers such as DTrace. It includes CTF, symbol/string tables, pseudo section headers for text/data/bss, filename, and private objfs info while avoiding export of actual text/data/bss contents.

## Main Entry Points
- `objfs_data_init()` builds the section-header string table and resolves section links.
- `objfs_create_data()` creates a GFS file vnode for an object’s `object` file and records module generation/primary status.
- `objfs_data_lock()` and `objfs_data_unlock()` hold/release the module while validating that the vnode still refers to the current module generation.
- `objfs_data_getattr()` reports the synthetic ELF file size.
- `objfs_data_open()` rejects writes.
- `objfs_data_read()` synthesizes the ELF header, section headers, section data, padding, and special symbol-table transformations.
- `objfs_tops_data[]` registers VOPs for the data file.

## Internal Mechanics
The file defines `section_desc_t` descriptors for dummy, `.shstrtab`, `.SUNW_ctf`, `.symtab`, `.strtab`, `.text`, `.data`, `.bss`, `.info`, and `.filename`. `SECT_DATA` descriptors store offsets into `struct module` fields rather than direct addresses. `sect_addr()`, `sect_size()`, and `sect_valid()` compute per-module section presence and layout.

`data_offset()` calculates the synthetic file layout: ELF header, valid section headers, then valid non-`SHT_NOBITS` section data with alignment. `next_offset()` and `data_size()` derive section boundaries and total file size from the same layout logic.

`objfs_data_read()` constructs a native 32-bit or 64-bit ELF header based on kernel build, sets endian/class/machine fields, uses `ET_SUNWPSEUDO`, emits only valid section headers, and then emits backing data for materialized sections. `.text`, `.data`, and `.bss` are represented as `SHT_NOBITS` with address/size metadata only. `.symtab` is copied symbol-by-symbol through `read_symtab()`, which rewrites defined symbols’ `st_shndx` to `SHN_ABS`.

## Dependencies
Uses GFS file helpers, kernel module loader structures, ELF headers, objfs internal node types, `mod_hold_by_modctl()`, `mod_release_mod()`, `uiomove()`, and kernel memory allocation.

## Risks and Notes
- Reads fail if the module was unloaded or reloaded after the data vnode was created, detected through `mod_gencount`.
- Layout code must keep section offsets, alignment, validity, and ELF header `e_shnum/e_shstrndx` consistent.
- The file intentionally exposes addresses and sizes for loaded module sections but not raw text/data/bss bytes.
