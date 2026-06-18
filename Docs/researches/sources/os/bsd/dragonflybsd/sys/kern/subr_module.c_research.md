# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_module.c

## Summary
Implements accessors and debug dumping for bootloader-provided preloaded module metadata.

## Main Responsibilities
- Stores global `preload_metadata`.
- Searches preloaded records by name, type, next name, or metadata attribute.
- Deletes a preloaded module record by marking fields `MODINFO_EMPTY`.
- Relocates physical pointers to kernel virtual addresses during bootstrap.
- Pretty-prints module metadata through `debug.dump_modinfo`.

## Important Behavior
Metadata is parsed as aligned TLV records with `u_int32_t` type/length headers. Name lookup compares both the full loader path and its basename. `preload_search_info()` stops when it loops back to the starting record type.

## Risks
All walkers assume well-formed loader metadata ending in zero headers. `preload_bootstrap_relocate()` only fixes known pointer-bearing fields. Deletion marks records empty but does not compact the metadata stream.
