# File Research: sources/os/bsd/netbsd-src/lib/libexecinfo/symtab.h

## Purpose
Private header for ELF symbol-table lookup support.

## Main Content
- Forward-declares `symtab_t`.
- Declares `symtab_destroy()`, `symtab_create()`, and `symtab_find()`.

## Integration
Used by `backtrace.c` and implemented by `symtab.c`.

## Risks / Notes
The header assumes `Dl_info` is already visible to consumers through included system headers.
