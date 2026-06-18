# File Research: sources/os/linux/linux/io_uring/alloc_cache.c

## Purpose
Implements a small reusable object allocation cache for io_uring internals.

## Main Functions
- `io_alloc_cache_init()`: allocates the pointer array and initializes cache limits, element size, and initial clear size.
- `io_alloc_cache_free()`: drains cached objects with a caller-supplied free function, then frees the pointer array.
- `io_cache_alloc_new()`: allocates a new object and zeroes the configured prefix.

## Important Design Points
- `io_alloc_cache_init()` returns `true` on failure and `false` on success.
- The cache stores object pointers in a `kvmalloc_array()` allocation.
- Only the initial `init_clear` bytes are zeroed for newly allocated objects.

## Cross-File Relationships
- Inline cache get/put helpers are in `alloc_cache.h`.
- Used by futex wait support in `futex.c` and other io_uring request/cache paths.

## Risks / Review Notes
- The inverted boolean return convention is easy to misuse.
- Freeing requires callers to supply a function compatible with cached object allocation.
