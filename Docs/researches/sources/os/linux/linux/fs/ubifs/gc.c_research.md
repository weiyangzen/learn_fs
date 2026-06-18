# File Research: sources/os/linux/linux/fs/ubifs/gc.c

## Purpose

`gc.c` implements UBIFS out-of-place garbage collection for logical eraseblocks (LEBs). It distinguishes data LEBs from index LEBs: data nodes are copied into the GC journal head and their TNC references are replaced, while index nodes are marked dirty so the next commit can rewrite the index and later release the old index LEB. The file also defines the commit hooks that make GC'd index LEBs safely reusable.

## Main Control Flow

The core entry point is `ubifs_garbage_collect()`. It is called with the commit lock held and the GC write-buffer empty. It first checks whether a commit should run, locks the GC head write-buffer, then repeatedly asks lprops for a dirty or empty candidate via `ubifs_find_dirty_leb()`. Each selected LEB is processed by `ubifs_garbage_collect_leb()`.

`ubifs_garbage_collect_leb()` handles three cases. If `free + dirty == leb_size`, the LEB is immediately freeable: lprops are updated and the block is either retained in `c->gc_lnum` or unmapped and returned. If scanning shows an index LEB, each index node is looked up and dirtied in the TNC with `ubifs_dirty_idx_node()`, then the LEB is added to `c->idx_gc` and marked as freed only after commit. Otherwise the function treats the LEB as data, moves live nodes with `move_nodes()`, syncs other write-buffers to protect recovery, updates lprops, bumps `c->gc_seq`, and either retains or unmaps the LEB.

`move_nodes()` prepares the GC head if needed with `switch_gc_head()`, filters and sorts scanned nodes using `sort_nodes()`, then repeatedly writes data nodes and non-data nodes into the GC head. Data nodes are kept in inode/block order for bulk-read behavior; inode and dent/xent nodes are ordered to favor useful packing and directory iteration locality. Authenticated mounts add an auth node after moved nodes.

## Important Helpers and State

`switch_gc_head()` syncs the current GC write-buffer, unmaps the reserved `c->gc_lnum`, adds it as a new GC bud in the log, and seeks the GC write-buffer to it. This links GC movement to the journal/log machinery.

`gc_sync_wbufs()` syncs all non-GC journal heads before freeing an LEB. This is a recovery invariant: an obsolete-making node may still sit in a write-buffer, so erasing the old LEB before that node reaches flash could lose data after an unclean unmount.

`ubifs_gc_start_commit()` unmaps non-index freeable LEBs, marks already GC'd index LEBs as unmap-ready, and records fully dirty/free index LEBs for post-commit unmapping. `ubifs_gc_end_commit()` performs those unmaps and updates lprops after commit. `ubifs_destroy_idx_gc()` and `ubifs_get_idx_gc_leb()` maintain the index-GC list for unmount and commit allocation.

## Dependencies

This file depends heavily on lprops categorization and accounting (`ubifs_find_dirty_leb()`, `ubifs_change_one_lp()`, `ubifs_return_leb()`), the scanner (`ubifs_scan()`), TNC lookup/update APIs (`ubifs_tnc_has_node()`, `ubifs_tnc_replace()`, `ubifs_dirty_idx_node()`), journal/log functions (`ubifs_add_bud_to_log()`), write-buffer I/O (`ubifs_wbuf_*()`), and authentication hashing.

## Invariants and Edge Cases

GC uses soft and hard movement limits. After `SOFT_LEBS_LIMIT`, index GC work can force `-EAGAIN` so commit can make progress; after `HARD_LEBS_LIMIT`, lack of progress becomes `-ENOSPC`. The dynamic `min_space` threshold starts at `dead_wm`, falls when retained GC makes progress, and rises toward `dark_wm` when a retained LEB does not free space. Error paths sync the GC write-buffer, switch UBIFS to read-only for unexpected failures, and return any taken LEB to lprops when possible.
