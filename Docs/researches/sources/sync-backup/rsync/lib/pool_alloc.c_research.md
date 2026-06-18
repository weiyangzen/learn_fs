# sources/sync-backup/rsync/lib/pool_alloc.c

Purpose: implements rsync's extent-based memory pool allocator for many small, same-lifetime allocations such as file-list data.

Important APIs/types/functions: `pool_create`, `pool_destroy`, `pool_alloc`, `pool_free`, `pool_free_old`, `pool_boundary`, and `pool_stats`; internal `struct alloc_pool`, `struct pool_extent`, `POOL_DEF_EXTENT`, `POOL_QALIGN_P2`, `MINALIGN`, `PTR_ADD`, and `PTR_SUB`.

Control flow: `pool_create` validates alignment, applies defaults, adjusts extent layout for `POOL_INTERN`, rounds extent size to allocation quantum, and records flags. `pool_alloc` rounds requested length, creates a new extent when the live extent lacks room, optionally zeroes it, places allocations from the high end of free space downward, updates stats, and calls the bomb callback on failure. `pool_free` records returned bytes, resets the live extent when fully free, frees non-live extents when all bytes become free/bound, or tracks trapped bytes in `bound`. `pool_free_old` frees all extents older than a boundary address and must not be mixed with `pool_free`. `pool_boundary` optionally forces a new extent and returns a marker for later `pool_free_old`. `pool_stats` writes allocator statistics and extent free/bound counts to a file descriptor.

State and persistence behavior: all state is heap-resident in the pool and its extent list. Stats track created/freed extents and bytes/calls allocated/freed. `POOL_CLEAR` zeroes allocations/extents on creation and some frees, but the allocator is not a secure scrubber. Destroying the pool frees all extents.

Dependencies/integration: includes `rsync.h` for allocation macros (`new0`, `new_array`, `new`), integer types, `snprintf`, and `write`. Used by file-list construction (`flist.c`) for efficient allocation.

Risks/test signals: `pool_free` trusts caller-supplied size and address, does not detect double-free precisely, and only frees an extent when accounting reaches the extent size. Mixing `pool_free` and `pool_free_old` is explicitly forbidden. Tests should cover alignment, `POOL_INTERN`/`POOL_PREPEND`, zero-length allocation, oversize allocation/bomb behavior, extent freeing, boundary freeing, stats output, and misuse scenarios under sanitizers.
