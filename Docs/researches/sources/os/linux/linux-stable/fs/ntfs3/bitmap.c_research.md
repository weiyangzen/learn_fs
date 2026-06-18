# File Research: sources/os/linux/linux-stable/fs/ntfs3/bitmap.c

This file implements ntfs3 bitmap-window management for cluster and MFT allocation bitmaps. It keeps cached free-space extents in red-black trees while retaining the ability to rescan on-disk bitmap blocks.

Main responsibilities:
- Initializes and destroys a slab cache for free-extent nodes.
- Builds two extent trees for free ranges: one sorted by start, one sorted by length.
- Rescans on-disk bitmap data to initialize or rebuild cached free extents and per-window free counts.
- Marks bitmap ranges free or used and updates buffer heads, per-window counters, total zero counts, and cached extents.
- Safely marks only actually-free bits as used for repair/reconciliation scenarios.
- Checks whether ranges are free or used, using trees when possible and bitmap buffers otherwise.
- Finds allocatable free ranges with hint support, full-or-partial semantics, zone exclusion, largest-extent fallback, optional mark-as-used, and bitmap scanning fallback.
- Extends a bitmap, used for `$MFT` bitmap growth.
- Temporarily excludes a zone from allocation with `wnd_zone_set()`.
- Implements filesystem trim by scanning free bitmap ranges and calling discard.
- Provides little-endian bitmap set, clear, and weight helpers.

Important functions and data:
- `struct e_node` stores one free extent in both start and count trees.
- `NTFS_MAX_WND_EXTENTS` caps cached extents at 32K; if exceeded, the cache keeps larger extents and marks exactness degraded.
- `wnd_scan()` scans a bitmap buffer window for a free run and tracks the best fragment.
- `wnd_add_free_ext()` merges adjacent free extents and inserts or replaces cached extent nodes.
- `wnd_remove_free_ext()` removes or splits cached extents after allocation.
- `wnd_rescan()` walks bitmap runs, reads mapped blocks, counts zero bits, and rebuilds extent metadata.
- `wnd_init()` allocates `free_bits`, computes window count and final-window bits, and performs the initial rescan.
- `wnd_set_free()` and `wnd_set_used()` mutate on-disk bitmap buffers and cached state.
- `wnd_find()` is the allocator-facing free-space search routine.
- `wnd_extend()` grows the bitmap and zeroes new bits.
- `ntfs_trim_fs()` implements `FITRIM`-style discard over free clusters.
- `ntfs_bitmap_set_le()`, `ntfs_bitmap_clear_le()`, and `ntfs_bitmap_weight_le()` operate on little-endian bitmap words.

Notable implementation details:
- `wnd->free_bits[iw]` caches the number of free bits per bitmap block/window.
- `wnd->uptodated` tracks whether extent trees are exact, empty, or degraded.
- The zone `[zone_bit, zone_end)` is removed from free extents and skipped by allocation searches.
- Readahead is used during full rescans of mapped bitmap storage.

Research notes:
- This file is the core ntfs3 free-space allocator cache; allocator correctness depends on keeping on-disk bitmaps, counters, and extent trees synchronized.
- When the extent cache is incomplete, searches can fall back to direct bitmap scanning.
