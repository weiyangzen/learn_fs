# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_module.c

## Purpose
Handles bootloader-preloaded module metadata: locating modules by name/type, fetching metadata attributes, deleting preload records, relocating pointers, and dumping decoded metadata.

## Main Interfaces
- `preload_initkmdp()`: locates kernel metadata and optionally panics if absent.
- Search helpers: `preload_search_by_name()`, `preload_search_by_type()`, `preload_search_next_name()`, `preload_search_info()`.
- Fetch helpers: `preload_fetch_addr()`, `preload_fetch_size()`.
- Mutation/relocation: `preload_delete_name()`, `preload_bootstrap_relocate()`.
- Diagnostics: `preload_dump()`, debug sysctl `debug.dump_modinfo`, DDB `show preload`.

## Implementation Notes
Metadata is TLV-like: a 32-bit type and 32-bit length followed by rounded-up data. Records begin with `MODINFO_NAME`; searches iterate until a zero type/length terminator. `preload_search_info()` scans within one record and stops when it loops to the initial metadata type.

`preload_delete_name()` marks fields as `MODINFO_EMPTY` and frees bootstrap memory when both address and size are found. `preload_bootstrap_relocate()` adjusts pointer-valued metadata after early physical-to-virtual relocation for known attributes.

Dump formatting decodes standard `MODINFO_*` and many `MODINFOMD_*` metadata types, printing strings, sizes, VM offsets, flags, or omitting raw buffers.

## Dependencies
Uses linker metadata definitions, machine metadata constants, `sbuf`, VM bootstrap free, sysctl, and DDB.

## Research Notes
This file influences boot-time module discovery for kernel components, including filesystem modules and boot resources. The parser assumes trusted bootloader-provided metadata and relies on terminators/alignment.
