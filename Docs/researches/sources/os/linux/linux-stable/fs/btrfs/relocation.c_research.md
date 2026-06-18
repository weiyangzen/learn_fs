# File Research: sources/os/linux/linux-stable/fs/btrfs/relocation.c

This file implements Btrfs block-group relocation, including the classic relocation-tree path and the newer remap-tree path. Relocation moves every extent out of a target block group so balance, shrink, profile conversion, compaction, and chunk/device operations can retire or repurpose the old block group.

Core model:
- `struct reloc_control` is the per-relocation state: target block group, extent root, data relocation inode, metadata block reservation, backref cache, file extent cluster, processed tree-block bitmap, reloc-root rb-tree/list, dirty subvolume list, reservation counters, search cursor, relocation stage, and flags for reloc-tree creation/merge.
- `struct mapping_tree` maps an original tree root bytenr to its relocation root.
- `struct tree_block` records a metadata extent to relocate, including bytenr, owner, first key, level, and whether the key was read.
- `struct file_extent_cluster` groups adjacent data extents so the data relocation inode can preallocate and write them with preserved extent boundaries.
- Relocation stages are `MOVE_DATA_EXTENTS` and `UPDATE_DATA_PTRS`.

Classic relocation flow:
- `btrfs_relocate_block_group()` is the main public entry point. It looks up the block group and extent root, waits for unfinished snapshot drops, rejects swapfile-pinned block groups, starts cancellable relocation state, makes the block group read-only, removes v1 free-space cache extents, creates a data relocation inode when the remap-tree feature is unavailable, waits for reservations/NOCOW/ordered roots, finishes zoned block groups, then dispatches to classic or remap-tree relocation.
- `do_nonremap_reloc()` repeatedly calls `relocate_block_group()`. In the first pass, data extents are copied through the data relocation inode. If data extents were found, it waits for ordered writes, invalidates the relocation inode mapping, and switches to `UPDATE_DATA_PTRS` so file extent items can be rewritten to the new physical locations.
- `relocate_block_group()` scans the committed extent tree from `rc->search_start` using `find_next_extent()`, skips already processed metadata ranges, collects tree blocks or data references, relocates tree blocks, copies data clusters, checks cancellation, handles `-EAGAIN` metadata-reservation retries, prepares reloc-root merging, merges reloc roots, commits pinned extents, cleans dirty subvolumes, and releases the temporary reservation.

Relocation roots:
- `create_reloc_root()` creates a `BTRFS_TREE_RELOC_OBJECTID` snapshot-like root item from a source root. It rejects partially dropped subvolumes, copies the source root node, initializes the root item, inserts it into the root tree, reads it back, and marks it shareable.
- `btrfs_init_reloc_root()` creates or updates a root's relocation root during transaction recording. It uses `rc->block_rsv` unless the transaction already has relocation reservation.
- `__add_reloc_root()`, `__del_reloc_root()`, and `__update_reloc_root()` maintain the in-memory rb-tree/list mapping from root block address to reloc root and carefully balance references held by `root->reloc_root` and `rc->reloc_roots`.
- `btrfs_update_reloc_root()` updates a reloc root item at transaction commit time, marks merged reloc trees dead when their refs reach zero, updates the rb-tree mapping when the root node changes, and persists the root item in the root tree.
- `find_reloc_root()` looks up a reloc root by original root bytenr for backref users.
- `btrfs_should_ignore_reloc_root()` tells backref lookup whether a stale reloc root from a previous transaction should be ignored.

Backref tree and metadata relocation:
- `build_backref_tree()` constructs a backref graph for a metadata block using `btrfs_backref_add_tree_node()` and finishes upper links. It also calls `handle_useless_nodes()` to detach or free orphaned backref nodes.
- `select_one_root()` decides whether a block can be relocated through a single root path or needs full relocation through multiple backrefs.
- `select_reloc_root()` walks a backref path to a shareable root, ensures a reloc root exists, records the relevant source root in the transaction, rewrites the backref-cache path to point at the reloc root, and marks processed roots.
- `do_relocation()` COWs or rewrites upper-level pointers so parents point to relocated blocks. It updates tree refs, drops old subtrees with `btrfs_drop_subtree()`, and keeps pending backref nodes linked until their parents are updated.
- `relocate_tree_block()` reserves metadata, selects the relocation strategy, updates processed state, and cleans backref cache nodes on errors or leaves.
- `relocate_tree_blocks()` reads missing first keys with readahead, handles COW-only trees and the data relocation tree without backref-tree construction, relocates all collected tree blocks, and then finishes pending nodes.

Reloc-root merge:
- `prepare_to_merge()` reserves worst-case merge metadata, sets `rc->merge_reloc_tree`, updates reloc-root refs so crash recovery can resume merging, and commits before the merge phase.
- `merge_reloc_roots()` repeatedly splices the reloc-root list, fetches each source root, merges roots with refs, or queues orphan reloc trees for cleanup when refs are zero.
- `merge_reloc_root()` walks modified blocks in a reloc tree and calls `replace_path()` to swap matching subtrees back into the filesystem tree. It records merge progress in `root_item.drop_progress`, refills reservations per iteration, updates extent caches for affected data ranges, and queues merged subvolumes on `dirty_subvol_roots`.
- `replace_path()` is the actual subtree swapper. It compares keys and generations, COWs the destination path if needed, records swapped qgroup blocks, swaps child block pointers between the fs tree and reloc tree, updates delayed refs for both trees, and returns the level replaced.
- `clean_dirty_subvols()` drops merged reloc snapshots or orphan reloc trees and clears `BTRFS_ROOT_DEAD_RELOC_TREE`.

Data relocation:
- `create_reloc_inode()` creates an unlinked regular inode in the data relocation root, marks it NOCOMPRESS/PREALLOC, records the relocated block group start, and adds it to orphan cleanup.
- `prealloc_file_extent_cluster()` invalidates cached pages for the relocation inode range, reserves data chunks, locks each clustered range, and preallocates replacement extents while preserving source extent sizes.
- `setup_relocation_extent_mapping()` installs a pinned extent map that maps relocation inode file offsets back to the source block group range for reading original data.
- `relocate_one_folio()` locks or creates the relevant folio, performs readahead unless RAID stripe tree remapping would make it unsafe, reads the original data, reserves delalloc metadata, marks cluster-covered ranges delalloc/dirty, sets `EXTENT_BOUNDARY` at source extent boundaries, throttles writeback, and checks cancellation.
- `relocate_file_extent_cluster()` drives preallocation, extent-map setup, and folio relocation across a cluster.
- `relocate_data_extent()` builds adjacent data extent clusters, flushing them when physical adjacency breaks, ownership changes under simple quotas, or `MAX_EXTENTS` is reached.
- `get_new_location()` looks up the data relocation inode file extent corresponding to an old physical data extent.
- `replace_file_extents()` runs during `UPDATE_DATA_PTRS` when a leaf is COWed. It rewrites file extent disk bytenrs to relocated locations, drops stale extent maps for live inodes, increments new data refs, and frees old data refs.
- `btrfs_reloc_clone_csums()` clones checksums from original data extents to ordered relocation extents, offsetting cloned checksum records to the new physical disk bytenr.

Remap-tree relocation:
- `should_relocate_using_remap_tree()` is defined in the header and selects remap-tree relocation only when the incompat feature exists and the block group is neither system nor metadata-remap.
- Remap-tree mode avoids the data relocation inode path. It records identity ranges for used portions of the source block group, copies bytes directly to new logical ranges, stores `BTRFS_REMAP_KEY` and `BTRFS_REMAP_BACKREF_KEY` records, and updates free-space/block-group accounting.
- `create_remap_tree_entries()` reads the free-space tree for the block group, converts used-space gaps into `BTRFS_IDENTITY_REMAP_KEY` entries, and records `bg->identity_remap_count`.
- `start_block_group_remapping()` caches free space, runs delayed refs so the free-space tree is current, creates identity remap entries, marks the block group and chunk as remapped, removes block-group free-space records/cache, and commits the setup.
- `do_remap_reloc_trans()` processes one identity remap range per transaction: reserves a new logical range, copies bytes, removes the destination from the free-space tree, converts the identity item into a remap item plus backref, accounts destination remap bytes, and marks the source fully remapped when identity entries are gone.
- `do_remap_reloc()` loops `do_remap_reloc_trans()` until no identity remaps remain.
- `move_existing_remaps()` and `move_existing_remap()` move remap destinations away from a block group that already contains remapped bytes before relocating that block group itself.
- `btrfs_translate_remap()` translates a logical range through `BTRFS_REMAP_KEY` or identity entries, trimming the supplied length to the mapped item boundary.
- `btrfs_remove_extent_from_remap_tree()` removes an allocated/freed range from a remapped block group's remap tree by punching holes in remap or identity items.
- `remove_range_from_remap_tree()` deletes or splits the affected remap item, removes matching backrefs, adjusts identity counts and destination `remap_bytes`, and returns the overlapped length consumed.
- `btrfs_last_identity_remap_gone()` completes a fully remapped chunk by removing device extents, updating devices, clearing chunk allocation bits, removing the block group from its space info, clearing stripe-removal state, truncating the chunk item stripes to zero, and committing.

Crash recovery and cancellation:
- `reloc_chunk_start()` and `reloc_chunk_end()` serialize cancellable relocation with `BTRFS_FS_RELOC_RUNNING` and `reloc_cancel_req`.
- `btrfs_should_cancel_balance()` checks balance cancellation, relocation cancellation, and fatal signals; it is also an error-injection hook.
- `btrfs_recover_relocation()` scans the root tree for `BTRFS_TREE_RELOC_OBJECTID` roots at mount/recovery time, marks garbage reloc roots with zero refs if their source root is gone, rebuilds `reloc_control`, reattaches live reloc roots to source roots, commits, merges reloc roots, cleans dirty subvolumes, and runs data relocation orphan cleanup when the remap-tree feature is not enabled.
- `mark_garbage_root()` clears drop progress and refs on a reloc root item so cleanup can drop it.

Snapshot and COW hooks:
- `btrfs_reloc_cow_block()` is called during tree block COW while relocation is active. For reloc roots, it validates the backref-cache path, attaches the new `extent_buffer` to the backref node, queues pending parent updates, marks first COWs processed, and accounts relocated node bytes. During `UPDATE_DATA_PTRS`, leaf COWs trigger `replace_file_extents()`.
- `btrfs_reloc_pre_snapshot()` increases snapshot metadata reservation when a snapshot is created during reloc-root merging.
- `btrfs_reloc_post_snapshot()` migrates reservation if needed and creates a reloc root for the new snapshot based on the source root's reloc tree.
- `btrfs_get_reloc_bg_bytenr()` returns the currently relocating block group start while `reloc_mutex` is held, or `U64_MAX` if no relocation is active.

Important dependencies:
- Backreference graph construction and cleanup from `backref.h`.
- Extent allocation/freeing and delayed refs from `extent-tree.h`.
- Root item insertion/update from `root-tree.h`.
- File extent manipulation from `file-item.h`.
- Block-group readonly, free-space cache/tree, RAID stripe tree, qgroup, zoned, and transaction subsystems.

Concurrency and locking:
- `fs_info->reloc_mutex` protects the global `fs_info->reloc_ctl` pointer and reloc-root list splicing against root transaction recording.
- `reloc_root_tree.lock` protects the rb-tree mapping from original root bytenr to reloc root.
- `cleaner_mutex` serializes classic block-group relocation with cleaner work.
- Remap-tree mutations are serialized by `fs_info->remap_mutex`.
- Data extent cache invalidation uses inode extent locks and `i_mmap_lock` trylocks to avoid racing reads and reflinks.
- Block group relocation waits for outstanding block-group reservations, NOCOW writers, and ordered roots before moving the block group.

Integrity and error handling:
- Many unexpected metadata states are treated as corruption with `-EUCLEAN`, including missing root paths, non-shareable roots in shared backref walks, reloc root mismatches, malformed extent items, and missing extent/csum roots.
- Transaction-aborting failures call `btrfs_abort_transaction()` after on-disk references have been modified.
- Metadata reservation pressure can return `-EAGAIN`, causing relocation to end the transaction, grow the temporary reservation, and retry.
- Classic relocation always enters prepare/merge cleanup even after cancellation so created reloc roots are orphaned and dropped consistently.

Role in the subsystem:
- This is the central implementation for moving Btrfs logical extents out of a block group while preserving metadata sharing, checksums, qgroup accounting, snapshots, backreferences, free-space state, zoned constraints, and crash recovery.
