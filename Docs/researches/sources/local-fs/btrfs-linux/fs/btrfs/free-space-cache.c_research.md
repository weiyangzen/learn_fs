# File Research: sources/local-fs/btrfs-linux/fs/btrfs/free-space-cache.c

## Summary
Implements Btrfs free-space cache v1 and the in-memory free-space allocator for block groups. It manages free-space extents and bitmap entries, loads and writes legacy cache inodes, allocates from free-space clusters, tracks discard/trim state, handles zoned block-group accounting, and provides sanity-test helpers.

## Main Responsibilities
- Create, find, truncate, write, validate, and remove per-block-group free-space cache inodes.
- Maintain `btrfs_free_space_ctl` rb-trees indexed by offset and available size.
- Represent free space as extent entries or sector-granularity bitmaps, converting small fragmented regions to bitmaps when thresholds are exceeded.
- Add, remove, merge, split, and search free-space ranges for extent allocation.
- Build and allocate from clustered free-space windows for metadata and SSD-spread allocation paths.
- Track discardable bytes/extents and trim state for sync and async discard.
- Implement block-group trimming over extent entries and bitmap entries.
- Provide special accounting behavior for zoned block groups, where free space follows allocation-pointer semantics rather than ordinary arbitrary reuse.

## Key APIs
- Cache inode lifecycle: `lookup_free_space_inode()`, `create_free_space_inode()`, `btrfs_remove_free_space_inode()`, `btrfs_truncate_free_space_cache()`.
- Cache I/O: `load_free_space_cache()`, `btrfs_write_out_cache()`, `btrfs_wait_cache_io()`.
- Free-space control: `btrfs_init_free_space_ctl()`, `btrfs_remove_free_space_cache()`, `btrfs_dump_free_space()`.
- Free-space updates: `btrfs_add_free_space()`, `btrfs_add_free_space_unused()`, `btrfs_add_free_space_async_trimmed()`, `btrfs_remove_free_space()`.
- Allocation: `btrfs_find_space_for_alloc()`, `btrfs_find_space_cluster()`, `btrfs_alloc_from_cluster()`, `btrfs_return_cluster_to_free_space()`, `btrfs_init_free_cluster()`.
- Discard/trim: `btrfs_is_free_space_trimmed()`, `btrfs_trim_block_group()`, `btrfs_trim_block_group_extents()`, `btrfs_trim_block_group_bitmaps()`, `btrfs_trim_fully_remapped_block_group()`.
- Space-cache v1 feature state: `btrfs_free_space_cache_v1_active()`, `btrfs_set_free_space_cache_v1_active()`.
- Slab lifecycle: `btrfs_free_space_init()`, `btrfs_free_space_exit()`.

## Important Behavior
The legacy on-disk cache is stored in an internal inode referenced by a `BTRFS_FREE_SPACE_OBJECTID` item. The cache file starts with page CRCs and a generation, then serializes free-space entries followed by bitmap pages. Loading validates inode generation, cache generation, CRCs, entry counts, duplicate entries, and total free-space accounting before copying the temporary cache into the live block group.

Writeout is asynchronous relative to transaction commit. `btrfs_write_out_cache()` serializes extents, bitmaps, pinned extents from the current transaction, and active trimming ranges, dirties the cache inode pages, and starts writeback. `btrfs_wait_cache_io()` later waits for ordered I/O, updates the cache header counts/generation, and marks the block group `BTRFS_DC_WRITTEN` only if it did not become dirty again.

The in-memory free-space cache uses two trees: `free_space_offset` for address lookup and `free_space_bytes` for largest-first allocation lookup. Extent and bitmap entries can share an offset; ordering makes normal extents preferred before bitmap entries. Bitmap entries maintain `bytes`, `bitmap_extents`, `max_extent_size`, and trim state.

Free-space insertion first tries to merge neighboring extent entries according to trim-state rules. If extent count pressure is high or regions are small/fragmented, space is inserted into bitmap entries. Large regions are forced back to extent entries, and adjacent bitmap ranges are stolen into new extent entries to improve future allocation success.

Allocation prefers extent entries and uses bitmap `max_extent_size` as a cached negative-search result. If alignment creates a leading gap, the gap is returned to free space after the allocation. Cluster allocation moves extents or bitmap entries out of the normal free-space tree into a `btrfs_free_cluster` tree, then allocates from the cluster under its own lock.

Trimming temporarily removes free space from the cache, records it in `trimming_ranges` so cache writeout does not lose it, issues `btrfs_discard_extent()`, then reinserts the range with trimmed or untrimmed state based on discard success. Bitmap trimming has lossy trimmed-state handling to avoid repeatedly discarding tiny fragments.

Zoned mode bypasses the normal tree/bitmap free-space model. Freeing space adjusts `ctl->free_space`, `block_group->alloc_offset`, and `zone_unusable`, and may mark block groups unused or reclaimable when unusable space crosses thresholds.

## State and Synchronization
`ctl->tree_lock` protects the free-space rb-trees, free-space counters, bitmap counts, and discardable counters. `ctl->cache_writeout_mutex` serializes cache writeout against trim operations that may remove bitmap ranges or manipulate `trimming_ranges`.

Block-group state is protected with `block_group->lock`, `data_rwsem`, and transaction dirty-list locks depending on the path. Cluster state is protected by `cluster->lock`, while cluster insertion/removal also occurs under the parent control's `tree_lock`.

Cache inode I/O uses page locks, extent locks, `EXTENT_DELALLOC`, ordered range waits, and inode generation updates. GFP masks deliberately avoid filesystem recursion for cache inode pages.

## Risks
The file has several overlapping accounting systems: free bytes, free extents, bitmap extents, discardable bytes, cache entries, pinned extents, trimming ranges, cluster contents, and zoned unusable space. Any missed update can lead to allocator ENOSPC errors, duplicate free-space exposure, leaked free space, or stale discard counters.

Cache v1 correctness depends on generation and CRC validation. A valid-looking but stale cache could corrupt allocation decisions, so the load path drops the entire temporary cache on mismatches, duplicates, or free-space total mismatches.

Lock ordering is subtle around `tree_lock`, cluster locks, `cache_writeout_mutex`, block-group locks, and transaction locks. The writeout and trim paths intentionally serialize only parts of the state to avoid losing ranges removed for discard.

Bitmap trim state is intentionally approximate. It optimizes async discard behavior but can cause retrimming or conservative untrimmed marking after races, interruption, or partial bitmap scans.

Zoned handling shares public free-space APIs but follows different semantics; callers must not assume arbitrary free-space tree entries exist in zoned mode.
