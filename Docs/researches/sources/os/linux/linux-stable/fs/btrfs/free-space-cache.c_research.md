# File Research: sources/os/linux/linux-stable/fs/btrfs/free-space-cache.c

## Purpose

Implements Btrfs free-space cache v1 and the runtime free-space cache used by block groups. It stores free space as extent entries or page-sized bitmaps, serializes/deserializes v1 cache inodes, provides allocation/removal helpers, manages allocation clusters, and drives synchronous/asynchronous discard trimming. It is the central in-memory allocator-side representation for non-zoned block groups, while zoned block groups take a specialized accounting path.

## Main Data Flow

- V1 cache inode lifecycle: `lookup_free_space_inode()`, `create_free_space_inode()`, `btrfs_remove_free_space_inode()`, and `btrfs_truncate_free_space_cache()` manage hidden per-block-group free-space cache inodes under the tree root.
- Cache read path: `load_free_space_cache()` validates block-group state, reads the cache inode into a temporary `btrfs_free_space_ctl`, verifies CRC/generation/space totals, then copies entries into the live block-group cache.
- Cache write path: `btrfs_write_out_cache()` serializes extents, bitmaps, pinned extents, and active trim ranges into the cache inode; `btrfs_wait_cache_io()` waits for writeback and marks the cache item valid.
- Allocation path: `btrfs_find_space_for_alloc()` searches by bytes or offset, handles full-stripe alignment gaps, clears bits/removes extents, updates discard accounting, and returns the chosen logical bytenr.
- Free path: `btrfs_add_free_space()`, `btrfs_add_free_space_unused()`, and `btrfs_add_free_space_async_trimmed()` add free regions, merge neighbors, choose extent vs bitmap representation, and queue async discard work when appropriate.
- Remove path: `btrfs_remove_free_space()` consumes free regions from extents or bitmaps, splitting/relinking extents as needed.
- Cluster path: `btrfs_find_space_cluster()`, `btrfs_alloc_from_cluster()`, and `btrfs_return_cluster_to_free_space()` move suitable extents/bitmaps into per-allocation clusters for less fragmented allocation.
- Trim path: `btrfs_trim_block_group()`, `btrfs_trim_block_group_extents()`, `btrfs_trim_block_group_bitmaps()`, and `btrfs_trim_fully_remapped_block_group()` discard free ranges while preserving free-space state and avoiding cache-write races.

## Internal Representation

The live cache is held by `struct btrfs_free_space_ctl` in two rbtrees: `free_space_offset` for bytenr ordering and `free_space_bytes` for largest-extent-first allocation. `struct btrfs_free_space` represents either a contiguous extent or a bitmap. Bitmap entries cover `BITS_PER_BITMAP * ctl->unit` logical bytes and track `bytes`, `max_extent_size`, `bitmap_extents`, and trim state. `entry_less()` intentionally sorts the bytes tree with larger available chunks first.

The code dynamically converts additions to bitmap-backed entries once the extent count exceeds memory thresholds. `recalculate_thresholds()` limits memory roughly by block-group size, while `use_bitmap()` keeps large extents as extents, avoids bitmaps for very small block groups, and includes debug fragmentation forcing. Large contiguous regions are also stolen back from adjacent bitmaps by `steal_from_bitmap*()` to improve allocation quality.

## On-Disk V1 Cache Format

`struct btrfs_io_ctl` walks cache-inode pages. Page 0 stores an array of per-page CRC32C values followed by the cache generation. Entries are written as `struct btrfs_free_space_entry` records, with bitmap payload pages appended after the entry list. `io_ctl_*` helpers map pages, read/write entries, add bitmap pages, zero trailing pages, and verify CRC/generation on load. `MAX_CACHE_BYTES_PER_GIG` and the first-page CRC/generation layout limit writable cache inode size.

## Concurrency And Locking

- `ctl->tree_lock` protects the free-space rbtrees, free-space counters, bitmap counters, and discardable counters.
- `ctl->cache_writeout_mutex` serializes cache writeout with trim bitmap/range manipulation and protects `trimming_ranges`.
- `block_group->lock`, `dirty_bgs_lock`, `data_rwsem`, and `cache_write_mutex` coordinate cache state transitions, dirty block groups, delalloc-sensitive data block groups, and cache truncation/writeback.
- Cluster operations use both `ctl->tree_lock` and `cluster->lock`; entries moved to clusters may have their bytes-index node cleared to prevent normal rbtree relinking.
- Cache inode lookup uses `memalloc_nofs_save()` and commit-root path flags in sensitive paths to avoid filesystem recursion and tree-root deadlocks.

## Error Handling And Integrity Checks

The load path rejects invalid inode generations, CRC mismatches, duplicate entries, zero-length entries, and free-space totals that do not match block-group accounting. Bad caches are cleared and rebuilt. Write failures invalidate inode pages, zero the inode generation, set `BTRFS_DC_ERROR`, and leave the caller responsible for aborting or retrying as appropriate. Many structural assumptions use `ASSERT()`/`WARN_ON()` because cache corruption or duplicate entries imply allocator metadata inconsistency.

## Zoned Behavior

For zoned filesystems the extent/bitmap free-space cache is bypassed. `__btrfs_add_free_space_zoned()` updates `ctl->free_space`, `alloc_offset`, and `zone_unusable`, and may mark block groups unused or reclaimable. `btrfs_remove_free_space()` advances `alloc_offset` during log replay if needed. Dumping reports free space after the allocation pointer.

## Integration Points

This file depends on block-group state, transaction commit state, extent-tree pinned extents, discard control, inode truncation/update helpers, page cache/folio operations, and mount options such as `DISCARD_SYNC`/`DISCARD_ASYNC`. It is used by allocation, block-group caching, transaction commit cache writeout, async discard, relocation/remapping cleanup, and Btrfs sanity tests.

## Test Hooks

Under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, `test_add_free_space_entry()` inserts exact extent/bitmap entries without normal merging, and `test_check_exists()` checks whether any free space overlaps a range. These are deliberately lower-level than production add/remove paths.
