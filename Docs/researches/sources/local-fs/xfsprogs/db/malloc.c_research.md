# File Research: sources/local-fs/xfsprogs/db/malloc.c

## Purpose
Provides xfs_db allocation wrappers that terminate consistently on out-of-memory.

## Main Interfaces
- `xcalloc()`, `xmalloc()`, `xrealloc()`, `xstrdup()`, and `xfree()`.

## Control Flow
Allocation wrappers call libc allocation functions, return successful results, or call `badmalloc()`, which prints an out-of-memory message and exits with status 4. `xmalloc()` uses `valloc()`.

## Dependencies
Uses `dbprintf()` and `progname` for diagnostics.

## Risks And Invariants
- These wrappers do not return on allocation failure.
- `xrealloc(ptr, 0)` follows libc semantics and can return NULL without treating it as an error.
