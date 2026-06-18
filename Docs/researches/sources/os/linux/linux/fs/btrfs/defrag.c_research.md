# File Research: sources/os/linux/linux/fs/btrfs/defrag.c

## Purpose

Implements Btrfs automatic inode defragmentation, metadata tree defragmentation, and user-requested file range defragmentation, including optional recompression or no-compression conversion.

## Main Responsibilities

- Maintain an rb-tree of inodes queued for autodefrag.
- Run batched autodefrag passes over queued inodes.
- Defragment B-tree leaves by reallocating out-of-order tree blocks.
- Find file extents eligible for defrag without permanently caching extent maps.
- Prepare folios safely for rewriting as delalloc.
- Collect mergeable target ranges for defrag.
- Mark target ranges dirty/delalloc/defrag so writeback rewrites them.
- Implement ioctl-facing file defrag range handling.
- Initialize and destroy the inode-defrag slab cache.

## Key Types And State

- `static struct kmem_cache *btrfs_inode_defrag_cachep`: slab cache for queued autodefrag records.
- `struct inode_defrag`:
  - rb-tree node,
  - inode number,
  - transaction id threshold,
  - root objectid,
  - extent-size threshold.
- `struct defrag_target_range`:
  - list node,
  - byte start,
  - byte length.

## Autodefrag Queue

- `compare_inode_defrag()` orders records by root objectid then inode number.
- `inode_defrag_cmp()` adapts comparison for `rb_find_add()`.
- `btrfs_insert_inode_defrag()` inserts or merges a queued inode record:
  - lowers stored transid if a newer insert refers to an older transaction,
  - keeps the smaller extent threshold,
  - sets `BTRFS_INODE_IN_DEFRAG`.
- `need_auto_defrag()` requires the mount option and rejects closing filesystems.
- `btrfs_add_inode_defrag()` queues an inode if autodefrag is active and the inode is not already queued.
- `btrfs_pick_defrag_inode()` removes the requested or next ordered record from the rb-tree.
- `btrfs_cleanup_defrag_inodes()` frees all queued records.
- `btrfs_run_defrag_inodes()` loops through queued records, respecting remount/closing state, and wakes `transaction_wait` on exit.
- `btrfs_run_defrag_inode()` resolves root+inode, defrags in batches of `BTRFS_DEFRAG_BATCH` sectors, and updates the next start offset.

## Metadata Tree Defrag

- `close_blocks()` tests whether two tree block addresses are within 32 KiB adjacency.
- `btrfs_realloc_node()` walks node children and force-COWs child blocks that are not close to neighbors, using allocation hints to improve disk locality.
- `btrfs_defrag_leaves()` walks shareable roots, tracks progress with `root->defrag_progress`, searches forward, locks level 1, and reallocates leaves under it.
- `btrfs_defrag_root()` serializes with `BTRFS_ROOT_DEFRAG_RUNNING`, runs transactions until completion or cancellation, balances dirty metadata, and returns `-EAGAIN` on cancellation.

## File Extent Discovery

- `defrag_get_extent()` searches the subvolume tree directly and creates a temporary extent map:
  - uses `btrfs_search_forward()` when `newer_than` is set,
  - can synthesize a hole extent map for gaps,
  - returns `NULL` when no matching extent exists,
  - avoids adding extent maps to the inode extent tree.
- `defrag_lookup_extent()` first tries the in-memory extent map tree, rejects merged extent maps, and falls back to `defrag_get_extent()` under extent locking if needed.
- `get_extent_max_capacity()` returns 128 KiB for compressed extents and filesystem max extent size otherwise.
- `defrag_check_next_extent()` decides whether the next extent makes the current small extent worth rewriting.

## Folio Preparation

- `defrag_prepare_one_folio()` obtains or creates a locked folio, rejects large folios unless experimental support is enabled, sets extent mapping state, waits for ordered extents in the folio range, reads the folio if needed, and returns it locked and uptodate.
- The function retries if the folio mapping/private state changes while waiting for ordered extents or reads.

## Target Collection And Rewrite

- `defrag_collect_targets()` scans a range and builds a list of target extents:
  - includes inline extents that should become regular extents,
  - skips holes and prealloc extents,
  - skips extents older than `newer_than`,
  - skips extents under writeback,
  - skips ranges already marked delalloc,
  - in compression/no-compression mode, targets all valid extents,
  - otherwise targets small extents that can merge with neighbors or target list ranges,
  - tracks `last_scanned_ret` so callers can skip invalidated or irrelevant ranges.
- `defrag_one_locked_target()` reserves delalloc space, clears/reapplies extent bits, marks folios dirty, and releases reserved extent accounting.
- `defrag_one_range()` prepares folios for a cluster subrange, waits for writeback, locks the extent range, recollects targets under lock, and marks each target for rewrite.
- `defrag_one_cluster()` collects targets without locks, performs readahead, invokes `defrag_one_range()` for each target, respects `max_sectors`, and updates scanned/defragged accounting.

## User/File Defrag Entry Point

`btrfs_defrag_file()` is the main file defrag API. It:

1. Validates file size and requested start.
2. Parses compression flags:
   - legacy `compress_type`,
   - extended `compress.type` and `compress.level`,
   - no-compress conversion.
3. Defaults extent threshold to 256 KiB.
4. Aligns the requested range to sectorsize.
5. Moves writeback index to the beginning of the range for sequential writeback.
6. Processes 256 KiB clusters.
7. Locks the inode around each cluster.
8. Rejects swapfiles and inactive superblocks.
9. Temporarily sets `inode->defrag_compress` and level for compression/no-compression conversion.
10. Calls `defrag_one_cluster()`.
11. Rate-limits dirty page balancing after progress.
12. Updates `range->start` for resumable autodefrag.
13. Optionally starts writeback immediately.
14. Sets incompat flags for LZO or ZSTD compression when used.
15. Clears temporary defrag compression state.

## Concurrency And Locking Notes

- Autodefrag rb-tree is protected by `fs_info->defrag_inodes_lock`.
- Running autodefrag count is tracked by `fs_info->defrag_running`.
- File defrag uses inode locking per cluster.
- Extent ranges are locked before final target validation and delalloc marking.
- Existing ordered extents are waited out before folios are reused.
- Metadata root defrag serializes per root through `BTRFS_ROOT_DEFRAG_RUNNING`.
- Cancellation uses `signal_pending(current)` through `btrfs_defrag_cancelled()`.

## Error Handling And Invariants

- Metadata defrag validates that COW uses the running transaction and filesystem generation, aborting on mismatch.
- `defrag_lookup_extent()` hides metadata lookup errors by returning `NULL` for `ERR_PTR()` extent maps.
- Large non-experimental folios return `-ETXTBSY`.
- File defrag returns negative errno for validation/errors, otherwise the number of sectors defragged.
- `range->start` is always advanced to support resumable autodefrag.
- If target collection allocation fails, all accumulated target ranges are freed.
- Swapfiles are rejected with `-ETXTBSY`.

## Dependencies

- Core tree search/COW APIs from `ctree.h`.
- Transaction APIs from `transaction.h`.
- Extent locking and subpage helpers from `extent_io.h`/`subpage.h`.
- Delalloc reservation from `delalloc-space.h`.
- File extent conversion helpers from `file-item.h`.
- Compression constants and validation from `compression.h`.
