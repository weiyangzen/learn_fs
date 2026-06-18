# File Research: sources/os/linux/linux/io_uring/alloc_cache.h

## Purpose
Defines the io_uring allocation cache API and inline fast paths.

## Main Contents
- `IO_ALLOC_CACHE_MAX` cap of 128 cached entries.
- Prototypes for cache init/free/new allocation.
- Inline helpers:
  - `io_alloc_cache_put()`: poisons and stores an object if capacity remains.
  - `io_alloc_cache_get()`: pops cached object and, under KASAN, unpoisons and clears the configured prefix.
  - `io_cache_alloc()`: get cached object or allocate new.
  - `io_cache_free()`: cache object or free it.

## Important Design Points
- KASAN mempool poisoning is integrated into cache put/get.
- Cached objects are not generally reinitialized unless KASAN is enabled; callers must ensure reused fields are reset or covered by `init_clear`.
- Overflow objects are freed via `kvfree()` in `io_cache_free()`.

## Cross-File Relationships
- Backed by `alloc_cache.c`.
- Used by `futex.c` for `struct io_futex_data` cache management.

## Risks / Review Notes
- Reuse safety depends on each user choosing a correct `init_clear` and clearing any state that must not persist.
- Mixing `kmalloc()` allocation with `kvfree()` is supported but should remain intentional.
