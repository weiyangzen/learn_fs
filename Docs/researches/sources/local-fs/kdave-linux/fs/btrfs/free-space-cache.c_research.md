# File Research: sources/local-fs/kdave-linux/fs/btrfs/free-space-cache.c

This file implements the old Btrfs free-space cache inode format, the in-memory free-space control used by block groups, allocator-facing free-space lookup, clustered allocation helpers, discard/trim state tracking, and v1 space-cache enable/cleanup.

Major responsibilities:
- Creates, finds, truncates, writes, reads, and removes per-block-group free-space cache inodes stored under `BTRFS_FREE_SPACE_OBJECTID`.
- Maintains an in-memory `btrfs_free_space_ctl` with offset and size rb-trees, extent entries, bitmap entries, free-space totals, discardable counters, and active trimming ranges.
- Converts between extent entries and page-sized bitmap entries to cap memory use while preserving fast large-extent allocation.
- Services allocator calls through `btrfs_find_space_for_alloc()`, `btrfs_find_space_cluster()`, and `btrfs_alloc_from_cluster()`.
- Handles synchronous and asynchronous discard trimming for normal extents, bitmap-backed free space, and fully remapped block groups.
- Provides zoned special cases where free-space accounting is based on block group allocation offset, zone capacity, and unusable bytes rather than rb-tree entries.

Old space-cache inode flow:
- `create_free_space_inode()` allocates an object id and calls `__create_free_space_inode()` to insert an inode item plus a free-space header item keyed by block group start.
- Free-space cache inodes are marked `NOCOMPRESS`, `PREALLOC`, `NODATASUM`, and `NODATACOW`; `lookup_free_space_inode()` also converts older inodes missing the latter flags and marks their cache clear.
- `load_free_space_cache()` first loads on-disk entries into a temporary control, validates generation, CRCs, entry counts, bitmap counts, and expected free-space total, then copies valid space into the block group's live control.
- `btrfs_write_out_cache()` serializes live free-space entries, cluster entries, active trimming ranges, and pinned extents into the cache inode; `btrfs_wait_cache_io()` waits for IO and updates the cache item generation/counts.
- `btrfs_truncate_free_space_cache()` drops cache inode extents, page cache, extent maps, and marks the block group's disk cache state clear.
- `btrfs_remove_free_space_inode()` orphans and unlinks the free-space cache inode/header item when removing the cache or disabling v1.

On-disk cache IO details:
- The cache inode is page-backed; the first page stores per-page CRC32C values followed by a cache generation.
- `btrfs_io_ctl` tracks locked pages, mapped page cursor, page count, entry count, and bitmap count.
- Entries are stored as `struct btrfs_free_space_entry` records, with bitmap payload pages written after the entry records.
- `io_ctl_prepare_pages()` allocates/locks page cache folios, marks them extent-mapped, reads existing pages when needed, and clears dirty state before writeout.
- CRC and generation mismatch turns the loaded cache into a rebuild path instead of trusting stale data.

In-memory free-space model:
- Free space is represented by `struct btrfs_free_space` entries, either plain extents or bitmap entries.
- `free_space_offset` supports offset lookup and neighbor merging; `free_space_bytes` is a cached rb-tree sorted with largest usable entry first.
- Bitmap entry size is `PAGE_SIZE * 8 * sectorsize` bytes of block group address space.
- `recalculate_thresholds()` limits memory to roughly `MAX_CACHE_BYTES_PER_GIG` and adjusts when bitmaps are added or removed.
- `link_free_space()` and `unlink_free_space()` maintain rb-trees, free-space totals, extent counts, and discardable counters.
- Bitmap helpers maintain `bytes`, `max_extent_size`, `bitmap_extents`, trim state, and bytes-index ordering.

Allocation behavior:
- `btrfs_add_free_space()` adds returned space as untrimmed unless sync discard is enabled; `btrfs_add_free_space_async_trimmed()` treats mount-time loaded space as trimmed when async or sync discard is active.
- New extents try to merge with adjacent entries, may be inserted into an existing/new bitmap, and may steal adjacent bitmap bits back into extent entries to improve allocator success.
- `btrfs_remove_free_space()` removes allocated ranges by splitting extent entries or clearing bitmap bits.
- `find_free_space()` can use the bytes-index for first-fit-by-size when allocation starts at block group start, otherwise walks by offset.
- Alignment to `full_stripe_len` is handled before returning an allocation, and any alignment gap is re-added with the original trim state.
- `btrfs_find_space_cluster()` builds clustered allocation windows from extent entries first and bitmap entries second; clusters are detached from the block group free-space rb-tree until returned.

Discard and trimming:
- `trim_no_bitmap()` trims extent entries and can do one async trim per invocation.
- `trim_bitmaps()` trims bitmap-backed regions, tracks bitmap trim progress with `BTRFS_TRIM_STATE_TRIMMING`, and can mark bitmap entries lossily trimmed for async discard filtering.
- `do_trimming()` temporarily reserves the range, performs `btrfs_discard_extent()`, then re-adds the trimmed or untrimmed free space while preserving non-trimmed leftovers.
- `trimming_ranges` prevents cache writeout from omitting space that is temporarily removed from the rb-tree while discard is in progress.
- `btrfs_trim_block_group()`, `btrfs_trim_block_group_extents()`, and `btrfs_trim_block_group_bitmaps()` freeze the block group during trim to prevent logical/physical reuse races.
- `btrfs_trim_fully_remapped_block_group()` advances the discard cursor for remapped groups and completes remapping once the full logical range is discarded.

Zoned handling:
- Zoned filesystems bypass normal rb-tree free-space operations.
- `__btrfs_add_free_space_zoned()` updates `ctl->free_space`, `alloc_offset`, and `zone_unusable` according to whether the freed region is beyond the write pointer or now unusable.
- When an entire zoned block group becomes unusable it is marked unused; when reclaimable unusable bytes cross the reclaim threshold it is marked for reclaim.
- `btrfs_remove_free_space()` only advances `alloc_offset` during log replay for zoned block groups, avoiding overwrite of tree-log nodes.

Concurrency and locking:
- `ctl->tree_lock` protects free-space rb-trees, counters, bitmap state, and trimming lists.
- `ctl->cache_writeout_mutex` serializes cache writeout with trimming and bitmap manipulation that can temporarily remove ranges.
- `block_group->lock`, `data_rwsem`, and `space_info->lock` protect block group state, data delalloc exclusion, reservations, and zoned counters.
- `cluster->lock` protects cluster rb-trees and cluster ownership.
- Transaction dirty block group state and cache IO list coordination happen through transaction locks and `cache_write_mutex` outside this file's local control.

Important invariants:
- Non-zoned free-space entries must not duplicate offset/type combinations in the offset rb-tree.
- For the v1 disk cache to be trusted, cache generation, CRCs, entry counts, bitmap counts, and computed free-space bytes must match the block group.
- Bitmap `max_extent_size` is cached only after scanning and is reset whenever bits are modified.
- Extent entries are preferred over bitmap entries for allocator efficiency, even if that means pulling contiguous bits out of bitmaps.
- Active trim ranges must be included in cache writeout to avoid losing free space across unmount/crash.
- Removed or remapped block groups short-circuit normal free-space operations where logical address reuse would be unsafe.
