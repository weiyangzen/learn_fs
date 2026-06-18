# File Research: sources/os/linux/linux/fs/btrfs/free-space-cache.c

## Purpose
Implements Btrfs free-space cache v1 and the in-memory free-space allocator state for block groups. It manages free ranges as a mix of extent entries and bitmap entries, supports cluster-based allocation, serializes/validates the v1 cache inode format, and drives sync/async discard trimming.

## Main Responsibilities
- Creates, looks up, truncates, writes, loads, and removes per-block-group free-space cache inodes.
- Maintains `struct btrfs_free_space_ctl` indexes:
  - `free_space_offset`: offset-ordered rb-tree.
  - `free_space_bytes`: size-ordered cached rb-tree.
- Stores free space as either `struct btrfs_free_space` extent entries or page-sized bitmaps.
- Converts small fragmented free ranges into bitmap entries when extent count pressure is high.
- Merges adjacent extent entries and can steal contiguous free ranges from neighboring bitmaps to improve allocator hit rate.
- Supports allocation from block-group free-space clusters for metadata and `ssd_spread` data allocation.
- Handles zoned Btrfs separately by updating allocation/unusable accounting rather than rb-tree entries.
- Handles discard trimming state, including async trim filters and in-progress trimming ranges.
- Initializes/destroys slab caches for free-space entries and bitmap pages.

## Key Data and Constants
- `BITS_PER_BITMAP = PAGE_SIZE * 8`: bits covered by each in-memory bitmap.
- `MAX_CACHE_BYTES_PER_GIG = 64K`: target memory budget per GiB of block-group free-space metadata.
- `FORCE_EXTENT_THRESHOLD = 1M`: large free ranges are kept as extents rather than bitmaps.
- `btrfs_free_space_cachep`: slab cache for `struct btrfs_free_space`.
- `btrfs_free_space_bitmap_cachep`: page-sized slab cache for bitmap data.
- `struct btrfs_trim_range`: temporary range tracked while discard is running so cache writeout does not lose removed ranges.

## Cache Inode Path
- `lookup_free_space_inode()` reuses a cached `block_group->inode` if present, otherwise finds the free-space inode through a `BTRFS_FREE_SPACE_OBJECTID` header item.
- `__create_free_space_inode()` creates a regular internal inode with `NOCOMPRESS`, `PREALLOC`, `NODATASUM`, and `NODATACOW`, then inserts the free-space header item pointing to that inode.
- `btrfs_remove_free_space_inode()` orphans and unlinks the cache inode, clears the block-group inode reference, and deletes the header item.
- `btrfs_truncate_free_space_cache()` truncates the cache inode to zero using `btrfs_truncate_inode_items()`, clears pagecache and extent maps, resets `disk_cache_state`, and aborts the transaction on failure.

## On-Disk V1 Cache I/O
`struct btrfs_io_ctl` abstracts cache inode page access.

Important helpers:
- `io_ctl_init()`, `io_ctl_free()`: allocate/free page vector.
- `io_ctl_prepare_pages()`: locks/creates pages and optionally reads them uptodate.
- `io_ctl_set_generation()` / `io_ctl_check_generation()`: store/check cache generation in the first page.
- `io_ctl_set_crc()` / `io_ctl_check_crc()`: per-page CRC32C validation; CRC slots are stored at the front of page 0.
- `io_ctl_add_entry()` / `io_ctl_read_entry()`: serialize free-space extent/bitmap descriptors.
- `io_ctl_add_bitmap()` / `io_ctl_read_bitmap()`: serialize bitmap payload pages.

Load/write flow:
- `__load_free_space_cache()` validates inode generation, header generation, CRCs, entry counts, bitmap count, then loads into a temporary free-space control.
- `load_free_space_cache()` only trusts caches with `BTRFS_DC_WRITTEN`, loads into a temporary control, checks free-space total against block-group accounting, then copies into the real control.
- `__btrfs_write_out_cache()` writes extent entries, in-progress trim ranges, pinned extents, then bitmap pages; dirty pages are flushed later.
- `btrfs_wait_cache_io()` waits for ordered writeback, updates the free-space header item, sets `BTRFS_DC_WRITTEN` or `BTRFS_DC_ERROR`, and drops the inode reference.

## In-Memory Free-Space Operations
Core rb-tree helpers:
- `tree_insert_offset()` inserts entries by logical offset. Extent and bitmap entries may share an offset, with extent entries ordered before bitmaps.
- `entry_less()` orders the size index with largest usable extent first.
- `tree_search_offset()` supports exact/fuzzy and bitmap-only lookup.
- `link_free_space()` and `unlink_free_space()` maintain both rb-trees plus free-space and discardable counters.

Bitmap operations:
- `offset_to_bit()`, `bytes_to_bits()`, `offset_to_bitmap()` translate logical offsets into bitmap location.
- `bitmap_clear_bits()` and `btrfs_bitmap_set_bits()` update bitmap bits, entry byte counts, cached max extent size, bitmap extent count, and discard stats.
- `search_bitmap()` finds a contiguous set-bit run; for allocation it uses cached `max_extent_size` to skip fragmented bitmaps.
- `insert_into_bitmap()` adds an incoming range into an existing or newly allocated bitmap when `use_bitmap()` says bitmap representation is preferable.
- `free_bitmap()` removes bitmap entries and adjusts thresholds/statistics.

Extent operations:
- `try_merge_free_space()` merges neighboring extent entries using trim-state-aware rules.
- `steal_from_bitmap_to_end()` and `steal_from_bitmap_to_front()` pull adjacent set bits out of bitmaps to grow extent entries.
- `steal_from_bitmap()` improves allocation quality by preferring large extent entries over split extent+bitmap representations.

Public mutation API:
- `btrfs_add_free_space()`: adds untrimmed free space, or zoned accounting if zoned.
- `btrfs_add_free_space_unused()`: adds space from unused regions; zoned mode may rewind `alloc_offset`.
- `btrfs_add_free_space_async_trimmed()`: used when loading/caching, marks free space trimmed if sync or async discard is enabled.
- `btrfs_remove_free_space()`: consumes a range from extents/bitmaps; zoned mode only advances `alloc_offset` for log replay safety.
- `btrfs_find_space_for_alloc()`: finds and removes an allocation candidate, handling alignment gaps by returning the gap to free space.

## Cluster Allocation
- `btrfs_init_free_cluster()` initializes a reusable allocation cluster.
- `btrfs_find_space_cluster()` builds a cluster from block-group free space, preferring extent entries and falling back to bitmap scanning.
- `setup_cluster_no_bitmap()` pulls qualifying extent entries into the cluster rb-tree.
- `setup_cluster_bitmap()` and `btrfs_bitmap_cluster()` locate sufficient free ranges inside bitmap entries.
- `btrfs_alloc_from_cluster()` allocates from a cluster and updates free-space/discard accounting.
- `btrfs_return_cluster_to_free_space()` moves cluster entries back to the owning block group and queues discard work.

## Discard and Trim
- `btrfs_is_free_space_trimmed()` checks whether all free-space entries in a block group are trimmed.
- `trim_no_bitmap()` trims extent entries.
- `trim_bitmaps()` trims bitmap-backed ranges, with lossy bitmap-level trim-state tracking to avoid repeatedly discarding small skipped ranges.
- `do_trimming()` temporarily reserves the range, calls `btrfs_discard_extent()`, re-adds the space with trimmed/untrimmed state, and removes the range from `trimming_ranges`.
- `btrfs_trim_block_group()`, `btrfs_trim_block_group_extents()`, and `btrfs_trim_block_group_bitmaps()` expose sync and async trim entry points.
- `btrfs_trim_fully_remapped_block_group()` handles remapped block groups during stripe removal/remap completion.

## Concurrency and Locking
- `ctl->tree_lock` protects free-space rb-trees and counters.
- `ctl->cache_writeout_mutex` serializes cache writeout with trim operations and protects bitmap payloads during writeout.
- `block_group->lock` protects block-group cache state and runtime flags.
- `cluster->lock` protects cluster rb-tree and block-group ownership.
- Cache inode lookup uses `memalloc_nofs_save()` to avoid filesystem recursion under transaction contexts.
- Cache read uses committed root search to avoid deadlock while loading cache during tree-root COW.

## Error Handling and Integrity
- Invalid cache generation, CRC mismatch, duplicate entries, or free-space total mismatch cause cache discard and rebuild.
- Transaction errors during cache truncation/removal/writeout abort transactions where required.
- `WARN_ON`, `ASSERT`, and critical logging flag internal invariant violations such as duplicate free-space entries.
- Test-only helpers under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` allow constructing unusual extent/bitmap states and querying range presence.

## Cross-File Links
- Uses `free-space-cache.h` for data structures and exported prototypes.
- Uses `inode-item.c` through `btrfs_truncate_inode_items()` for cache inode truncation.
- Interacts with block-group, transaction, discard, extent-tree, and file writeback code.
