# File Research: sources/local-fs/btrfs-linux/fs/btrfs/relocation.c

This file implements Btrfs block-group relocation. It supports the classic relocation-root/data-relocation-inode algorithm and the newer remap-tree path used when the `REMAP_TREE` incompat feature is enabled for eligible non-system, non-metadata-remap block groups.

Core concepts:
- A `reloc_control` tracks the block group being relocated, extent root, temporary metadata reservation, data relocation inode, backref cache, processed-block state, relocation-root mapping tree, dirty subvolume roots, current data cluster, merge reservation accounting, stage, and mode flags.
- Classic relocation has two data stages: `MOVE_DATA_EXTENTS` moves data bytes into a data relocation tree inode; `UPDATE_DATA_PTRS` updates file extent items to point at the new physical extents.
- Relocation roots are special `BTRFS_TREE_RELOC_OBJECTID` snapshots of fs roots. They hold relocated tree blocks until merge time, when subtrees are swapped back into the real roots.
- The remap-tree path records logical remappings in `fs_info->remap_root` using identity-remap, remap, and remap-backref items instead of rewriting every tree/file reference in the source block group immediately.

Primary public entry points:
- `btrfs_relocate_block_group()` is the main balance/shrink relocation entry. It waits for unfinished drops, makes the target block group read-only, deletes v1 free-space cache data, waits for reservations/NOCOW/ordered IO, finishes the zone if needed, and dispatches either remap-tree relocation or classic relocation.
- `btrfs_recover_relocation()` resumes interrupted relocation after mount by finding relocation roots in the tree root, reattaching them to their fs roots, merging them, cleaning dirty subvolumes, and cleaning the data relocation tree orphan inode for non-remap-tree filesystems.
- `btrfs_init_reloc_root()` creates or refreshes a relocation root when a shareable root is recorded in a transaction during relocation.
- `btrfs_update_reloc_root()` persists relocation-root root items at transaction commit and marks dead relocation trees during merge.
- `btrfs_reloc_cow_block()` is the COW hook used by ctree code to connect newly COWed blocks to relocation backref-cache nodes and, during data-pointer update, rewrite file extent items in newly COWed leaves.
- `btrfs_reloc_clone_csums()` clones existing checksums from the old data extent range into ordered checksums for relocated data.
- `btrfs_reloc_pre_snapshot()` and `btrfs_reloc_post_snapshot()` integrate snapshot creation with in-progress relocation-root merging.
- `btrfs_translate_remap()` translates logical reads through remap-tree items and clamps the requested length to the current remap record.
- `btrfs_remove_extent_from_remap_tree()` removes a freed range from remap-tree records and repairs/splits surrounding mappings.
- `btrfs_last_identity_remap_gone()` handles the point where a remapped chunk has no remaining identity ranges, removing dev extents, clearing chunk allocation bits, detaching the block group from its space info, and truncating chunk stripes.

Classic relocation flow:
- `prepare_to_relocate()` allocates a temporary block reservation, initializes search state, sets `fs_info->reloc_ctl`, joins and commits a transaction so relocation roots can be created consistently.
- `find_next_extent()` scans the commit-root extent tree over the target block group, skipping processed metadata ranges.
- Tree extents are gathered with `add_tree_block()` or `__add_tree_block()`, which derive level, generation, and sometimes owner from extent items/inline refs.
- Data extents are clustered by `relocate_data_extent()` and migrated through `relocate_file_extent_cluster()`, which preallocates matching destination extents, installs pinned extent maps, reads folios, marks delalloc ranges, preserves extent boundaries, and waits for writeback before pointer update.
- `relocate_tree_blocks()` readaheads missing tree blocks, resolves their first keys, and relocates each block through either a COW-only path for non-fs/data-reloc trees or a full backref-tree path for fs trees.
- `build_backref_tree()` builds a breadth-first backref graph from a target tree block to roots, using the backref cache and pruning useless nodes.
- `relocate_tree_block()` chooses whether a block can be handled by root replacement or needs `do_relocation()`, reserving enough metadata first.
- `do_relocation()` COWs or links relocated blocks into upper blocks, updates delayed refs, manages pending backref-cache nodes, and asserts that reservation failures have been prehandled.
- `prepare_to_merge()` marks relocation roots as mergeable/orphaned depending on prior errors, reserves merge metadata, and commits state so recovery can resume.
- `merge_reloc_roots()` and `merge_reloc_root()` walk relocation trees, use `replace_path()` to swap unchanged subtrees between reloc and fs roots, record qgroup swapped-block state, save progress in `drop_progress`, invalidate extent maps after data pointer replacement, and queue dead relocation roots for cleanup.
- `clean_dirty_subvols()` drops merged or orphan relocation roots with `btrfs_drop_snapshot()` and clears root relocation state.

Data pointer and cache handling:
- `replace_file_extents()` scans a leaf for non-inline file extent items pointing into the target block group, drops in-memory extent maps for live regular inodes where possible, replaces disk bytenrs with the data relocation inode’s new locations, and updates old/new data refs.
- `get_new_location()` looks up the matching file extent in the data relocation inode and validates size and encoding assumptions.
- `delete_v1_space_cache()` and `delete_block_group_cache()` remove v1 space-cache inodes whose data extents would otherwise block data relocation.
- `invalidate_extent_cache()` drops affected extent maps after relocated file extent leaves are swapped back into fs roots.

Remap-tree relocation flow:
- `start_block_group_remapping()` caches the block group, runs delayed refs so the free-space tree is current, creates initial identity-remap items from free-space tree holes, marks the chunk and block group as remapped, removes block-group free-space records, and removes the old free-space cache.
- `create_remap_tree_entries()` converts free-space extent/bitmap records into identity-remap ranges representing currently used logical space.
- `do_remap_reloc()` repeatedly calls `do_remap_reloc_trans()` to find the next identity-remap range, reserve a destination logical range, physically copy data with remap bios, remove destination free-space records, replace the identity range with remap/backref items, and mark the source block group fully remapped when the identity count reaches zero.
- `copy_remapped_data()` copies data in bounded chunks using `copy_remapped_data_io()`; remap bios set `bbio->is_remap` and use completion/refcount tracking in `reloc_io_private`.
- `move_existing_remaps()` and `move_existing_remap()` move remap-tree entries that already point into a block group being relocated again, including physical copy, remap/backref updates, free-space tree updates, and remap byte accounting.
- `adjust_block_group_remap_bytes()` and `adjust_identity_remap_count()` update block-group remap counters, dirty block groups in the transaction, and mark unused or fully-remapped block groups when counters reach zero.
- `remove_range_from_remap_tree()` deletes or splits identity/remap records around a hole, removes backrefs for non-identity mappings, updates destination remap bytes, and returns the removed overlap length.

Concurrency and cancellation:
- `reloc_chunk_start()`/`reloc_chunk_end()` serialize cancellable relocation through `BTRFS_FS_RELOC_RUNNING` and `reloc_cancel_req`.
- `set_reloc_control()`/`unset_reloc_control()` publish or clear `fs_info->reloc_ctl` under `reloc_mutex`.
- Remap-tree mutations are serialized with `fs_info->remap_mutex`.
- Classic relocation takes `cleaner_mutex` around `relocate_block_group()` so cleaner/drop interactions stay ordered.
- `btrfs_should_cancel_balance()` checks balance cancellation, relocation cancellation, and fatal signals, and is explicitly error-injection enabled.

Error handling and invariants:
- Many structural inconsistencies return `-EUCLEAN` with diagnostics, especially missing roots, mismatched relocation roots, malformed backrefs, or impossible remap-tree state.
- Mutations after reference changes abort the transaction on failure.
- Relocation-root lifetime is reference-count sensitive: relocation roots can be held by `root->reloc_root`, `rc->reloc_roots`, dirty cleanup lists, and recovery lists.
- Processed tree blocks are tracked in an extent IO tree to avoid duplicate relocation work.
- Simple quota mode records the source owner root on the data relocation root so replacement allocations are attributed to the eventual owner.
- Qgroup subtree-swap accounting is deliberately delayed by recording swapped blocks before exchanging fs and relocation subtrees.
- Remap-tree block groups must maintain coherent `remap_bytes`, `identity_remap_count`, free-space tree contents, chunk flags, and block-group runtime flags.
