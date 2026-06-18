# File Research: sources/local-fs/btrfs-linux/fs/btrfs/defrag.c

## Purpose

Implements Btrfs automatic inode defragmentation, explicit file defragmentation, and B-tree leaf defragmentation/reallocation.

## Main Responsibilities

- Maintains an rbtree of inodes queued for autodefrag.
- Runs autodefrag in bounded batches.
- Reallocates B-tree leaf blocks to improve key-order/disk-order locality.
- Locates file extents that are eligible for defrag.
- Prepares folios and extent locks for defrag writeback.
- Marks target ranges delalloc/defrag so normal writeback rewrites them.
- Handles optional compression or no-compression defrag modes.
- Initializes and destroys the inode defrag slab cache.

## Key Data And State

- `btrfs_inode_defrag_cachep`: slab cache for `struct inode_defrag`.
- `struct inode_defrag`: rbtree node keyed by root objectid and inode number, with transid and extent threshold.
- `struct defrag_target_range`: linked-list entry for a contiguous file range selected for defrag.
- `BTRFS_DEFRAG_BATCH`: autodefrag sector limit per inode pass, 1024.
- `CLUSTER_SIZE`: explicit file defrag cluster size, 256 KiB.

## Important Functions

- Autodefrag queue:
  - `btrfs_add_inode_defrag()` queues an inode when autodefrag is enabled.
  - `btrfs_pick_defrag_inode()` removes the next inode defrag record from the rbtree.
  - `btrfs_cleanup_defrag_inodes()` frees queued records.
  - `btrfs_run_defrag_inodes()` drains queued inode records.
  - `btrfs_run_defrag_inode()` performs bounded passes on one inode.
- Tree defrag:
  - `btrfs_defrag_root()` loops transactions while leaf defrag reports progress.
  - `btrfs_defrag_leaves()` searches shareable roots and advances `root->defrag_progress`.
  - `btrfs_realloc_node()` COWs children whose physical block positions are not close to neighbors.
- File extent discovery:
  - `defrag_get_extent()` searches the subvolume tree without caching extent maps and can skip older generations.
  - `defrag_lookup_extent()` tries the extent map tree first, then metadata lookup under extent lock.
  - `defrag_collect_targets()` builds target ranges from valid, mergeable, non-hole, non-prealloc, non-delalloc extents.
  - `defrag_check_next_extent()` checks whether defragging the current extent can merge with the following extent.
- File defrag execution:
  - `defrag_prepare_one_folio()` locks/creates a folio, waits for ordered extents, and reads it uptodate.
  - `defrag_one_locked_target()` reserves delalloc space and sets defrag/delalloc bits plus dirty folio state.
  - `defrag_one_range()` prepares folios, locks extent state, revalidates targets, and marks them.
  - `defrag_one_cluster()` collects target ranges, triggers readahead, and processes bounded ranges.
  - `btrfs_defrag_file()` is the public ioctl/autodefrag entry point.

## Control Flow

Autodefrag queues are keyed by root and inode. When an inode is added, its oldest relevant transaction ID and smallest extent threshold are preserved. `btrfs_run_defrag_inodes()` repeatedly picks records, resolves roots and inodes, clears the in-memory defrag flag, and calls `btrfs_defrag_file()` with a sector batch cap. The updated range start allows subsequent passes to resume.

Explicit file defrag validates the requested range and compression flags, aligns the range to sectors, sets writeback position for sequential IO, then processes 256 KiB clusters. For each cluster it collects candidate extents, starts readahead, prepares and locks folios, revalidates under extent lock, marks target ranges as delalloc/defrag, dirties folios, and lets normal writeback rewrite the data.

Tree defrag operates only on shareable roots. It searches forward from stored progress, COW-reallocates level-1 child leaf blocks whose block addresses are not near adjacent leaves, stores progress when more work remains, and repeats transactions until complete or cancelled.

## Integration Points

- Uses core B-tree APIs from `ctree.c`, especially `btrfs_search_forward()`, `btrfs_search_slot()`, `btrfs_find_next_key()`, and `btrfs_force_cow_block()`.
- Uses extent map helpers to interpret file extents and detect holes, inline extents, compression, preallocation, generations, and merge state.
- Uses ordered extent APIs to avoid racing existing writeback.
- Uses delalloc reservation and extent state bits to hand defrag writes to the normal writeback path.
- Uses compression helpers to validate defrag compression levels and set per-inode defrag compression state.
- Uses superblock write guards for autodefrag writes.

## Invariants And Risks

- Autodefrag is skipped when the mount option is disabled or the filesystem is closing/remounting.
- Defrag avoids swapfiles and inactive superblocks.
- It skips prealloc extents, holes, old extents below `newer_than`, extents already under writeback, and ranges already delalloc.
- Large readonly THP folios are rejected unless experimental Btrfs is enabled.
- Target collection is re-run under extent lock because extents may change after the first scan.
- Delalloc reservation happens while the range is locked only after checking for existing delalloc to avoid deadlocks.
- Compression mode is stored temporarily in the inode and reset after the operation.
- Tree defrag requires a transaction matching filesystem generation, otherwise aborts as corruption.

## Testing Notes

Coverage should include autodefrag queue duplicate merging, mount option disable/remount/unmount behavior, explicit defrag with range boundaries, holes, inline extents, compressed extents, prealloc extents, delalloc overlap, ordered extent waits, swapfile rejection, compression and no-compression flags, `START_IO` flushing, max-sector throttling, and tree defrag progress/cancellation.
