# File Research: sources/os/linux/linux-stable/fs/btrfs/defrag.c

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

## Autodefrag Queue
Queued records are `struct inode_defrag`, ordered by root objectid then inode number. `btrfs_add_inode_defrag()` queues an inode only when autodefrag is enabled and the filesystem is not closing. Reinserted records merge by lowering the stored transaction id and keeping the smaller extent threshold.

`btrfs_run_defrag_inodes()` removes queued records in order, resolves root+inode, and calls `btrfs_defrag_file()` in batches of `BTRFS_DEFRAG_BATCH` sectors. It tracks running defraggers with `fs_info->defrag_running` and wakes `transaction_wait` on exit.

## Metadata Tree Defrag
`btrfs_realloc_node()` walks node children and force-COWs child blocks that are not close to neighbors, using allocation hints to improve disk locality. `btrfs_defrag_leaves()` walks shareable roots, tracks progress with `root->defrag_progress`, searches forward, locks level 1, and reallocates leaves. `btrfs_defrag_root()` serializes per root with `BTRFS_ROOT_DEFRAG_RUNNING`, runs transactions until completion/cancellation, and returns `-EAGAIN` if cancelled.

## File Defrag
`defrag_get_extent()` searches the subvolume tree directly and creates a temporary extent map, optionally using `btrfs_search_forward()` to skip extents older than `newer_than`. `defrag_lookup_extent()` first tries the in-memory extent map tree, rejects merged extent maps, then falls back to metadata lookup.

`defrag_prepare_one_folio()` obtains a locked folio, rejects large folios unless experimental support is enabled, waits for ordered extents, reads the folio if needed, and returns it locked and uptodate.

`defrag_collect_targets()` skips holes, prealloc extents, old extents, writeback extents, and delalloc ranges. In compression/no-compression mode it targets all valid extents; otherwise it targets small extents that can merge with neighboring target ranges. `defrag_one_locked_target()` reserves delalloc space, updates extent bits, marks folios dirty, and releases reservation accounting.

`btrfs_defrag_file()` validates range and compression flags, aligns to sectorsize, processes 256 KiB clusters, locks the inode per cluster, rejects swapfiles, temporarily sets `inode->defrag_compress` and level, optionally starts writeback, and updates `range->start` for resumable autodefrag.

## Risks And Invariants
- Autodefrag rb-tree is protected by `fs_info->defrag_inodes_lock`.
- Extent ranges are locked before final target validation and delalloc marking.
- Existing ordered extents are waited out before folios are reused.
- Large non-experimental folios return `-ETXTBSY`.
- File defrag returns negative errno for errors, otherwise the number of sectors defragged.
- If target collection allocation fails, accumulated target ranges are freed.
- Swapfiles are rejected with `-ETXTBSY`.
