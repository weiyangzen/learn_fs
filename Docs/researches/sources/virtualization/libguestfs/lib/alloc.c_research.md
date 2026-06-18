# File Research: sources/virtualization/libguestfs/lib/alloc.c

## Role
Implements libguestfs internal allocation wrappers that abort through the handle’s abort callback on allocation failure.

## Main Helpers
- `guestfs_int_safe_malloc()`
- `guestfs_int_safe_calloc()` with overflow protection for non-GNU calloc implementations.
- `guestfs_int_safe_realloc()`
- `guestfs_int_safe_strdup()`
- `guestfs_int_safe_strndup()`
- `guestfs_int_safe_memdup()`
- `guestfs_int_safe_asprintf()`

## Design
The wrappers centralize out-of-memory behavior and avoid repeated error-path handling in internal library code.

## Filesystem/Storage Relevance
Indirect but broad: all host-side filesystem, launch, drive, and protocol code relies on these allocation helpers.
