# File Research: sources/os/linux/linux/fs/btrfs/relocation.c

## Purpose

This file implements Btrfs block group relocation, including classic relocation through relocation trees/data relocation inode, crash recovery of unfinished relocation, snapshot hooks during relocation, checksum cloning for relocated data, and the newer remap-tree relocation path.

Relocation is used by balance, device/chunk profile conversion, shrink, and space compaction. Its job is to evacuate all extents from a target block group so the group can be deleted, remapped, or reused.

## Main Entry Points

- `btrfs_relocate_block_group()`: top-level relocation of one block group.
- `btrfs_recover_relocation()`: mount-time recovery for interrupted reloc-tree merging.
- `btrfs_init_reloc_root()`: creates a relocation tree for a filesystem root when it is dirtied during relocation.
- `btrfs_update_reloc_root()`: persists and retires relocation roots.
- `btrfs_reloc_cow_block()`: transaction-time hook called when CoW creates a relocated tree block.
- `btrfs_reloc_clone_csums()`: clones checksums for data relocation ordered extents.
- `btrfs_reloc_pre_snapshot()` / `btrfs_reloc_post_snapshot()`: snapshot integration while relocation roots are being merged.
- `btrfs_translate_remap()`: translates logical addresses through the remap tree.
- `btrfs_remove_extent_from_remap_tree()`: removes freed/deallocated ranges from remap metadata.
- `btrfs_last_identity_remap_gone()`: finalizes chunk stripe removal once identity remaps are gone.
- `btrfs_get_reloc_bg_bytenr()`: reports the currently relocating block group.

## Core State

- `struct reloc_control` is the central per-block-group relocation controller. It stores:
  - target `block_group`
  - relevant `extent_root`
  - temporary data relocation inode
  - relocation block reservation
  - backref cache
  - clustered data extent relocation state
  - processed tree block tracking
  - mapping from original root bytenr to reloc root
  - lists of active reloc roots and dirty subvolume roots
  - reservation accounting and relocated-node accounting
  - current relocation stage
  - flags controlling creation and merge of relocation trees

- `enum reloc_stage` has two phases:
  - `MOVE_DATA_EXTENTS`: copy/move data extents into new locations through the data relocation inode.
  - `UPDATE_DATA_PTRS`: update file extent items to point at the copied data.

- `struct mapping_tree` / `struct mapping_node` map a root block address to its relocation root.
- `struct tree_block` represents a metadata extent selected for relocation.
- `struct file_extent_cluster` batches adjacent data extents so relocation can preallocate and write them efficiently.
- `struct space_run` is used by remap-tree relocation to convert free-space tree records into occupied identity-remap ranges.
- `struct reloc_io_private` tracks synchronous read/write bio completion for remap-tree data copying.

## Classic Relocation Flow

`btrfs_relocate_block_group()`:
- Looks up the block group and extent root.
- Rejects relocation if the filesystem is closing, the block group is pinned by a swapfile, or unfinished snapshot drops are still pending.
- Allocates `reloc_control`.
- Marks relocation as running with `reloc_chunk_start()`.
- Makes the target block group read-only with `btrfs_inc_block_group_ro()`.
- Deletes any v1 free-space cache inode for the block group.
- Creates a temporary data relocation inode unless the remap-tree feature is active.
- Waits for block group reservations, nocow writers, ordered roots, and zoned block group finishing.
- Chooses either classic relocation (`do_nonremap_reloc()`) or remap-tree relocation.
- On failure, restores block group read-write state if needed and releases relocation state.

Classic relocation repeats until no extents remain:
- `relocate_block_group()` prepares state and scans the target extent range.
- `find_next_extent()` scans the commit-root extent tree for unprocessed extent items inside the block group.
- Tree extents are recorded with `add_tree_block()`.
- Data extents are batched with `relocate_data_extent()` during `MOVE_DATA_EXTENTS`.
- During `UPDATE_DATA_PTRS`, `add_data_references()` finds all leaves referencing data extents and relocates those leaves so file extent pointers can be rewritten.
- `prepare_to_merge()` marks reloc roots ready for merge or orphan cleanup.
- `merge_reloc_roots()` swaps relocated blocks into their real filesystem roots.
- `clean_dirty_subvols()` drops merged or orphaned reloc trees.

## Relocation Roots

A relocation root is a special snapshot-like root with `BTRFS_TREE_RELOC_OBJECTID` and key offset equal to the original root id.

Creation and tracking:
- `create_reloc_root()` copies the source root node, prepares a root item, inserts it into the root tree, reads it back as a root, and marks it shareable.
- `btrfs_init_reloc_root()` creates one relocation root per shareable filesystem root when relocation is active and reloc-tree creation is enabled.
- `__add_reloc_root()` inserts the reloc root into `rc->reloc_root_tree` and `rc->reloc_roots`.
- `find_reloc_root()` looks up a reloc root by original root node bytenr.
- `__update_reloc_root()` updates the address mapping when the reloc root node changes.
- `__del_reloc_root()` removes the rb-tree/list entry and drops the list reference.
- `btrfs_update_reloc_root()` persists the reloc root item and marks dead reloc trees during merge.

Important state rules:
- `BTRFS_ROOT_DEAD_RELOC_TREE` means the reloc tree has been merged and should generally be ignored.
- `reloc_root_is_dead()`, `have_reloc_root()`, and `btrfs_should_ignore_reloc_root()` provide safe visibility checks with memory barriers.
- Reloc roots are not independently recorded in transaction roots the same way normal roots are; their corresponding filesystem roots are recorded and reloc root last-trans is updated explicitly.

## Backref Tree Construction

Relocation needs complete knowledge of what references a tree block.

- `build_backref_tree()` builds a backref tree rooted at a target tree block by repeatedly calling `btrfs_backref_add_tree_node()` and finishing upper links.
- `walk_up_backref()` follows the first upper edge path to a root.
- `walk_down_backref()` finds the next reference path.
- `handle_useless_nodes()` removes orphaned or detached nodes from the backref cache and marks them processed.
- `mark_block_processed()` records relocated/processed tree blocks in `rc->processed_blocks`.
- `update_processed_blocks()` marks a node and every upper block that directly or indirectly references it.
- `tree_block_processed()` checks whether a bytenr is already processed.

Corruption defenses:
- Missing root paths, non-shareable roots on shared paths, mismatched reloc roots, duplicate mapping entries, or inconsistent bytenrs generally return `-EUCLEAN`, `-EINVAL`, or abort the transaction.
- Several paths use `ASSERT()` for internal invariants but still return errors for possible on-disk corruption.

## Metadata Relocation

Tree blocks are relocated by creating relocation roots for affected roots, CoWing blocks into those roots, and later swapping pointers back.

Key functions:
- `add_tree_block()` parses extent items to determine tree block level, generation, and likely owner.
- `__add_tree_block()` searches the extent tree for a metadata item and adds it unless already processed.
- `relocate_tree_blocks()` readaheads tree blocks, fills missing first keys, and relocates each block.
- `relocate_tree_block()` chooses whether the block resolves to a root block or needs normal lower-block relocation.
- `select_one_root()` determines whether a block has exactly one usable root path or is shared.
- `select_reloc_root()` selects the relocation root for a backref path and updates cached node state.
- `do_relocation()` CoWs or pointer-updates all upper nodes that reference a target node.
- `link_to_upper()` finishes pending CoW nodes.
- `finish_pending_nodes()` drains pending nodes level by level.
- `relocate_cowonly_block()` handles non-fstree/COW-only trees and the data relocation tree by CoWing down to a block without full backref-tree generation.

Reservation logic:
- `calcu_metadata_size()` estimates nodes needed for one relocation.
- `reserve_metadata_space()` and `refill_metadata_space()` reserve metadata from `rc->block_rsv`.
- `-EAGAIN` is used when reservation needs a full flush outside the current transaction.

## Reloc Root Merge

`merge_reloc_root()` merges one relocation tree back into its corresponding filesystem tree:
- Walks relocated blocks in the reloc root using `walk_down_reloc_tree()` and `walk_up_reloc_tree()`.
- Uses `replace_path()` to swap unchanged filesystem tree pointers with relocated pointers.
- Records progress in `root_item.drop_progress` and `root_drop_level` so recovery can resume.
- Invalidates extent cache ranges after data pointer replacement.
- Finally CoWs the filesystem root node to handle single-root-block relocation and queues the subvolume for cleanup via `insert_dirty_subvol()`.

`replace_path()`:
- Traverses the destination filesystem tree and source reloc tree for the same key.
- Only swaps blocks that have not been modified since the reloc root snapshot.
- Updates block pointers and generations in both trees.
- Adds and drops delayed refs for both old and new tree blocks.
- Calls qgroup swapped-block tracking so quota accounting can rescan affected subtrees later.

`prepare_to_merge()`:
- Computes merge reservation size.
- Marks reloc roots with refs so recovery knows merging was in progress.
- Sets `rc->merge_reloc_tree`.
- Commits a transaction before actual merge.

`merge_reloc_roots()`:
- Processes all relocation roots.
- Merges roots with nonzero refs.
- Queues zero-ref/orphan reloc roots for deletion.
- Handles new reloc roots that may appear while the list is being processed.

## Data Relocation

Classic data relocation uses a temporary inode in the data relocation tree.

Setup:
- `create_reloc_inode()` creates a zero-link orphan inode in `data_reloc_root`.
- `__insert_orphan_inode()` inserts the inode item with regular-file mode and no-compress/prealloc flags.
- The inode’s `reloc_block_group_start` maps file offsets back to original logical addresses.

Moving data:
- `relocate_data_extent()` builds clusters of adjacent data extent keys, preserving cluster ownership for simple quotas.
- `prealloc_file_extent_cluster()` invalidates stale cache, reserves data space, and preallocates ranges with boundaries matching original extent sizes.
- `setup_relocation_extent_mapping()` installs a pinned extent map pointing file offsets to original disk bytenrs.
- `relocate_file_extent_cluster()` initializes readahead, prepares mapping, and writes clustered folios.
- `relocate_one_folio()` reads original data, marks the corresponding range delalloc/dirty, sets extent boundaries to prevent merging, and throttles writeback.

Updating pointers:
- `get_new_location()` looks up the relocation inode’s file extent item and returns the new disk bytenr.
- `replace_file_extents()` runs during `UPDATE_DATA_PTRS` on relocated leaves and changes file extent disk bytenrs from old block group addresses to new addresses.
- It drops extent maps for in-memory inodes, increments refs for new extents, and frees refs for old extents.

Checksum handling:
- `btrfs_reloc_clone_csums()` copies checksums from the original logical range into the ordered extent for the new data, adjusting checksum logical offsets for partially written prealloc extents.

Cancellation:
- `btrfs_should_cancel_balance()` checks balance cancel requests, relocation cancel requests, and fatal signals.
- It is error-injection enabled.
- `reloc_chunk_start()` and `reloc_chunk_end()` serialize cancellable relocation and clear cancel requests.

## Free Space Cache Handling

Before relocating a block group:
- `lookup_free_space_inode()` is used by the caller path to find the v1 free-space cache inode.
- `delete_block_group_cache()` truncates/deletes block group cache data.
- `delete_v1_space_cache()` detects v1 free-space cache file extents in the root tree that point into the block group and deletes the corresponding cache inode.
- This avoids free-space cache extents blocking data relocation.

## Remap-Tree Relocation

When `REMAP_TREE` is enabled and the block group is eligible, relocation avoids classic reloc roots/data reloc inode and instead builds remap metadata.

Eligibility is declared in `relocation.h`:
- remap tree feature must be enabled
- system block groups are excluded
- metadata-remap block groups are excluded

Remap-tree concepts:
- `BTRFS_IDENTITY_REMAP_KEY` maps an old logical range to itself.
- `BTRFS_REMAP_KEY` maps an old logical range to a new logical address stored in `struct btrfs_remap_item`.
- `BTRFS_REMAP_BACKREF_KEY` maps a new logical address back to the old logical address.
- `bg->identity_remap_count` tracks remaining unmoved occupied ranges.
- `bg->remap_bytes` tracks bytes in a destination block group that belong to remap entries.
- `BTRFS_BLOCK_GROUP_REMAPPED`, `BLOCK_GROUP_FLAG_FULLY_REMAPPED`, and `BLOCK_GROUP_FLAG_STRIPE_REMOVAL_PENDING` track remap/chunk state.

Starting remap relocation:
- `start_block_group_remapping()` caches the block group, runs delayed refs so the free-space tree is current, creates identity remap entries for all occupied space, marks the chunk remapped, removes block group free space from the free-space tree, and drops free-space cache.
- `create_remap_tree_entries()` scans the free-space tree under `free_space_lock` and converts holes into occupied identity-remap ranges.
- `parse_bitmap()` expands bitmap free-space entries into merged free-space runs.
- `add_remap_tree_entries()` batch-inserts remap-tree keys.

Moving remap ranges:
- `do_remap_reloc()` loops over transactions.
- `do_remap_reloc_trans()` finds the next identity remap, reserves a new logical extent elsewhere, copies bytes from old to new, removes new space from the free-space tree, adds a remap entry/backref, accounts destination `remap_bytes`, and marks the source block group fully remapped when identity entries are exhausted.
- `copy_remapped_data()` copies in bounded chunks using allocated pages.
- `copy_remapped_data_io()` submits remap-marked bios and waits synchronously.
- `reloc_endio()` completes remap I/O and records status.

Moving existing remaps:
- `move_existing_remaps()` evacuates existing remap backrefs from a block group before remapping it.
- `move_existing_remap()` allocates a new destination, copies data from an existing remapped location, updates/removes old remap/backref items, adds new backrefs, updates free-space-tree records, and adjusts `remap_bytes`.

Maintaining remap entries:
- `add_remap_item()` inserts an old-to-new remap.
- `add_remap_backref_item()` inserts a new-to-old remap backref.
- `add_remap_entry()` replaces part of an identity remap with a real remap and updates identity count.
- `insert_remap_item()` inserts either identity or real remap plus backref.
- `remove_range_from_remap_tree()` punches a range out of an identity/remap item, splits surrounding pieces, removes backrefs, adjusts destination remap bytes, and frees destination space as needed.
- `btrfs_remove_extent_from_remap_tree()` loops over remap items covering a deallocated range and removes the range while holding `remap_mutex`.
- `btrfs_translate_remap()` resolves logical reads through the remap tree, truncating the requested length to the current remap item boundary.

Chunk finalization:
- `adjust_identity_remap_count()` updates identity count and marks a block group fully remapped.
- `adjust_block_group_remap_bytes()` updates destination remap byte accounting and marks unused groups when appropriate.
- `mark_chunk_remapped()` sets `BTRFS_BLOCK_GROUP_REMAPPED` in both the in-memory chunk map and on-disk chunk item.
- `remove_chunk_stripes()` truncates the chunk item so it has zero stripes.
- `btrfs_last_identity_remap_gone()` removes device extents, updates devices, clears chunk allocation bits, removes the block group from space info, clears stripe-removal-pending state, removes chunk stripes, and commits.

## Recovery

`btrfs_recover_relocation()`:
- Scans the root tree for `BTRFS_TREE_RELOC_OBJECTID` root items.
- Reads all relocation roots and marks them shareable.
- For reloc roots with refs, verifies the corresponding filesystem root exists.
- If the filesystem root is gone, `mark_garbage_root()` marks the reloc root with zero refs so it can be dropped.
- Allocates a relocation control and sets it globally.
- Reattaches reloc roots to their filesystem roots using `__add_reloc_root()`.
- Commits, runs `merge_reloc_roots()`, commits again, and cleans dirty subvols.
- If classic relocation is active, runs orphan cleanup for the data relocation tree.

Crash-resume state is stored primarily in reloc root refs and `drop_progress`/`root_drop_level`.

## Snapshot Integration

- `btrfs_reloc_pre_snapshot()` adds extra metadata reservation when a snapshot is created while reloc roots are being merged.
- `btrfs_reloc_post_snapshot()` migrates reservation from the pending snapshot reservation into relocation’s block reservation, creates a reloc root for the newly created snapshot, tracks it in the relocation root mapping, and attaches it to the new root.
- This preserves relocation consistency across snapshots created during merge.

## Transaction and Locking Model

Important synchronization:
- `fs_info->reloc_mutex` protects `fs_info->reloc_ctl` and reloc root list splicing.
- `rc->reloc_root_tree.lock` protects bytenr-to-reloc-root rb-tree mappings.
- `fs_info->remap_mutex` serializes remap tree updates.
- `cleaner_mutex` serializes classic relocation with cleaner operations.
- `BTRFS_FS_RELOC_RUNNING` serializes cancellable relocation state.
- Extent locks and inode mmap locks protect data extent cache invalidation and relocation writes.
- Block group locks protect remap/identity counters and flags.
- Free-space locks protect block group free-space tree scanning.

Transaction rules:
- Many failures after metadata references are changed abort the transaction.
- Several paths deliberately commit between phases to ensure recoverable relocation state.
- Metadata reservations are explicitly managed with temporary block reservations to avoid unexpected `ENOSPC`.

## Important Invariants

- A target block group is made read-only before relocation scans and moves extents.
- All reloc roots must either be merged or queued for snapshot deletion.
- Classic relocation must finish data writeback before switching from `MOVE_DATA_EXTENTS` to `UPDATE_DATA_PTRS`.
- Destination data extents must preserve source extent boundaries; `EXTENT_BOUNDARY` prevents unwanted merging.
- `btrfs_reloc_cow_block()` must never run for the data relocation root during `UPDATE_DATA_PTRS`.
- Backref cache paths must correspond to the block being CoWed; mismatches indicate corruption or cache bugs.
- Remap-tree updates must keep old-to-new entries, new-to-old backrefs, free-space-tree state, block group remap bytes, and identity-remap counts consistent.
- For remap-tree metadata groups, non-data allocations are aligned down to `nodesize`.

## Dependencies

This file depends heavily on:
- Extent tree and delayed refs for ref updates.
- Backref walking/cache code.
- Transaction and root-tree update APIs.
- Free-space tree/cache APIs.
- Qgroup accounting and swapped-block tracking.
- Ordered extent/writeback and checksum logic.
- Block group, chunk map, device extent, zoned, and RAID stripe tree helpers.
- B-tree path/search/COW primitives.

## Risk Notes

This is one of the highest-risk Btrfs metadata files. It combines live transaction state, backreference correctness, data writeback, qgroup accounting, crash recovery, and block group/chunk metadata mutation. The main failure risks are stale or incomplete backrefs, missed extent refs during pointer swaps, wrong relocation root association, remap-tree/free-space-tree divergence, incorrect handling of partially completed merges, and cancellation/error paths leaving reloc roots or remap entries inconsistent.
