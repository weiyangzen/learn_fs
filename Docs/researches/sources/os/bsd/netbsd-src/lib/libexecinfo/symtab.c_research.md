# File Research: sources/os/bsd/netbsd-src/lib/libexecinfo/symtab.c

## Purpose
Loads ELF symbol tables from the current executable and finds nearest function symbols for backtrace formatting.

## Main Components
- Internal `struct symbol` stores symbol name, value, and info.
- Internal `struct symtab` stores sorted symbols and whether the ELF file is PIE (`ET_DYN`).
- `symtab_create()` initializes libelf, opens an ELF descriptor from fd, reads the ELF header, scans sections for `SHT_SYMTAB`, filters symbols by bind/type, duplicates names, sorts by address, and returns a `symtab_t`.
- `symtab_find()` binary-searches the sorted table for the closest preceding symbol and updates `Dl_info` when the symtab result is closer than `dladdr()`'s symbol.
- `symtab_destroy()` frees symbol names, symbol array, and table.

## Integration
Called by `backtrace_symbols_fmt()` to improve symbol names and offsets beyond `dladdr()`.

## Risks / Notes
- Only reads `SHT_SYMTAB`, not dynamic-only symbol tables.
- PIE handling subtracts `dli_fbase` before comparing addresses.
- Error paths warn and return `NULL`, allowing callers to continue with weaker symbolization.
