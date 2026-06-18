# File Research: sources/local-fs/ntfs-3g/libntfs-3g/misc.c

## Purpose
Small allocation wrapper module that logs allocation failures consistently.

## Main Interfaces
- `ntfs_calloc(size)` calls `calloc(1, size)` and logs failure.
- `ntfs_malloc(size)` calls `malloc(size)` and logs failure.
- `ntfs_realloc(ptr, size)` calls `realloc()` and logs failure.
- `ntfs_free(p)` wraps `free()`.

## Integration Points
Used across libntfs-3g for allocation with logging through `logging.c`.

## Risks
Wrappers do not alter allocation semantics. `ntfs_realloc()` returns `NULL` on failure and leaves original pointer ownership with the caller, matching standard `realloc()`.
