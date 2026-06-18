# File Research: sources/os/linux/linux/fs/btrfs/extent-tree.c

## Purpose

`extent-tree.c` implements core Btrfs extent-tree operations: extent lookup, backreference maintenance, delayed reference replay, extent allocation/freeing, block pinning/unpinning, discard/trim, tree-block allocation, and subvolume/snapshot tree deletion.

This file is not only an allocator. It is the main bridge between logical Btrfs metadata/data references, block-group accounting, transaction delayed refs, quota/simple-quota accounting, free-space trees, zoned allocation constraints, tree-log replay allocation, relocation/remapping, and snapshot deletion.

## Major Responsibilities

- Lookup data and metadata extent items in the correct extent root.
- Decode and validate inline extent backrefs.
- Insert, update, and remove inline and keyed backrefs for data extents and tree blocks.
- Queue and run delayed refs for extent reference count changes.
- Insert reserved data and metadata extent records into the extent tree.
- Allocate free logical ranges from block groups using clustered or zoned policies.
- Pin extents until transaction commit and return them to free space afterward.
- Discard/trim block-group free space and unallocated device ranges.
- Allocate initialized tree blocks and attach delayed extent refs.
- Drop snapshots/subtrees while preserving shared-tree backref correctness.
- Maintain qgroup/simple-quota deltas during allocation, freeing, replay, and subtree deletion.

## Backreference Model

The file documents and implements Btrfs backreference rules.

Data extents can have:
- Inline `BTRFS_EXTENT_DATA_REF_KEY` refs for normal root/objectid/file-offset ownership.
- Inline or keyed `BTRFS_SHARED_DATA_REF_KEY` refs when referenced through a parent tree block.
- Optional `BTRFS_EXTENT_OWNER_REF_KEY` inline owner refs for simple quota mode.

Tree blocks can have:
- `BTRFS_TREE_BLOCK_REF_KEY` for implicit root-owned references.
- `BTRFS_SHARED_BLOCK_REF_KEY` for full backrefs through a parent block.
- Skinny metadata items (`BTRFS_METADATA_ITEM_KEY`) or older full extent items.

Important helpers:
- `btrfs_get_extent_inline_ref_type()` validates inline ref type against expected data/tree context.
- `hash_extent_data_ref()` produces the key offset hash for implicit data refs.
- `lookup_inline_extent_backref()` finds or positions inline backrefs, falling back with `-EAGAIN` when the extent item is too full.
- `setup_inline_extent_backref()` inserts an inline ref and updates extent refs.
- `update_inline_extent_backref()` increments/decrements inline ref counts and removes zero-count refs.
- `lookup_extent_backref()` searches inline refs first, then keyed refs.
- `insert_extent_data_ref()`, `remove_extent_data_ref()`, `insert_tree_block_ref()`, and `lookup_tree_block_ref()` handle non-inline backref items.

The code is defensive around corrupted extent items: it validates item sizes, rejects impossible zero refs, prints leaves on serious mismatches, and aborts transactions on extent-tree inconsistency.

## Delayed References

Btrfs queues many extent reference changes as delayed refs and processes them later in transaction context.

Main flow:
- `btrfs_inc_extent_ref()` queues metadata or data delayed refs for new references.
- `btrfs_free_extent()` queues drops, except tree-log blocks are pinned directly.
- `btrfs_run_delayed_refs()` processes queued delayed ref heads.
- `__btrfs_run_delayed_refs()` selects delayed ref heads, merges compatible refs, and processes a bounded byte amount or all pending refs.
- `btrfs_run_delayed_refs_for_head()` drains individual delayed ref nodes from one head.
- `run_one_delayed_ref()` dispatches to tree or data handlers.
- `cleanup_ref_head()` removes empty heads and releases delayed-ref accounting.

Data refs:
- `run_delayed_data_ref()` either inserts a newly reserved file extent, increments an existing extent ref, or frees an extent ref.
- Insert-reserved paths call `alloc_reserved_file_extent()` and then record simple-quota deltas.

Tree refs:
- `run_delayed_tree_ref()` handles reserved tree-block insertion, normal ref increments, normal ref drops, and remap-tree drops.
- Tree block delayed refs are expected to have `ref_mod == 1`.

Delayed extent ops:
- `btrfs_set_disk_extent_flags()` queues an extent-op to set on-disk extent flags.
- `__run_delayed_extent_op()` applies flags and tree-block keys to extent items.
- `run_delayed_extent_op()` searches the on-disk item, including skinny-metadata fallback, and updates it.

Accounting:
- `btrfs_cleanup_ref_head_accounting()` releases delayed-ref reservation state, pending checksum accounting, and simple-quota reservations.
- `free_head_ref_squota_rsv()` frees simple-quota data reservation attached to a delayed ref head.

## Extent Freeing

`__btrfs_free_extent()` is the core on-disk extent reference drop path. It locates the target inline or keyed backref, finds the corresponding extent item, decrements refs, removes backref records, and deletes the extent item when the final ref is gone.

If the last ref is removed:
- Data checksums are deleted with `btrfs_del_csums()`.
- RAID stripe tree entries are deleted with `btrfs_delete_raid_extent()`.
- Simple-quota deletion deltas are recorded, using an owner ref when present.
- The logical range is added back to the free-space tree unless remap handling already did it.
- Block-group used accounting is decremented.

If refs remain:
- The extent item ref count is updated.
- The matching inline/keyed backref is decremented or removed.
- Delayed extent ops may update flags/key metadata.

`check_ref_cleanup()` opportunistically removes an empty delayed ref head when freeing a tree block’s last delayed ref.

## Pinning, Unpinning, and Commit-Time Space Return

Pinning prevents freed extents from being reused before the current transaction is safely committed.

Key functions:
- `pin_down_extent()` updates block-group and space-info pinned/reserved counters and records the range in transaction `pinned_extents`.
- `btrfs_pin_extent()` pins a logical range.
- `btrfs_pin_extent_for_log_replay()` pins log-tree blocks during replay after ensuring the free-space cache is populated and removing the range from free space.
- `btrfs_pin_reserved_extent()` pins an already reserved tree block.
- `unpin_extent_range()` returns pinned ranges to free space or accounts them as readonly/zone-unusable depending on block-group state and zoned mode.
- `btrfs_finish_extent_commit()` discards pinned ranges if requested, clears dirty pinned states, unpins ranges, schedules async discard, and handles deleted block groups.

`btrfs_error_unpin_extent_range()` is an error-context helper that unpins without returning free space and ignores errors.

## Discard and Trim

Discard helpers operate at several layers:

- `btrfs_issue_discard()` issues block-device discard while aligning to sectors, chunking requests, and skipping Btrfs superblock mirror ranges.
- `do_discard_extent()` maps one discard stripe, using zone reset on zoned filesystems when possible and mirroring reset to device-replace targets if needed.
- `btrfs_discard_extent()` maps a logical range to one or more device stripes and discards each writable stripe.
- `btrfs_trim_fs()` implements FITRIM: it trims free space in each block group, then trims unallocated device ranges.
- `btrfs_trim_free_extents_throttle()` trims unallocated device extents in bounded chunks and records `CHUNK_TRIMMED`.
- `btrfs_trim_free_extents()` iterates devices by UUID order and tolerates per-device errors while returning the first error.

Trim continues across block groups/devices after non-interrupt errors, but exits on user interruption.

## Free Extent Exclusion for Tree Log Replay

Tree-log replay may reference extents that appear free from the current allocator perspective.

- `__exclude_logged_extent()` removes a logged extent from a block group’s free-space cache.
- `btrfs_exclude_logged_extents()` scans a log leaf for disk-backed file extent items and excludes them, used especially for mixed block groups.
- `btrfs_alloc_logged_file_extent()` records a replayed logged file extent, reserves block-group bytes, inserts an extent item/backref, removes it from free space when needed, and records simple-quota deltas.

## Cross-Reference Detection

`btrfs_cross_ref_exist()` checks whether a data extent has references other than a specific inode/offset.

It combines:
- `check_committed_ref()`, which inspects the committed extent item and inline ref layout.
- `check_delayed_ref()`, which checks delayed refs under the delayed-ref head mutex while the extent-tree leaf remains locked.

The function intentionally allows false positives to stay cheap on write paths, but avoids false negatives by coordinating extent-tree and delayed-ref locking.

## Extent Reference Modification for Tree Blocks

`__btrfs_mod_ref()` walks a tree block and queues ref increments or decrements for all child pointers or file extents it owns.

Public wrappers:
- `btrfs_inc_ref()` queues increments.
- `btrfs_dec_ref()` queues decrements.

For leaves, it skips non-file-extent items, inline file extents, and holes. For internal nodes, it queues metadata refs for child blocks. Relocation buffers use full-backref semantics as needed.

## Block Group Remapping and Fully Remapped Groups

This file participates in block-group remapping cleanup:

- `btrfs_complete_bg_remapping()` finishes remapping by removing chunk/device extent state and marking an empty block group unused.
- `btrfs_handle_fully_remapped_bgs()` drains `fully_remapped_bgs`, discards old ranges, completes remapping, and drops block-group references.
- `drop_remap_tree_ref()` returns remap tree references to the free-space tree and block-group accounting.

## Extent Allocation

`btrfs_reserve_extent()` is the public allocator entry point. It initializes a `find_free_extent_ctl`, chooses data or metadata allocation profile, detects tree-log and data-relocation allocation modes, and calls `find_free_extent()`.

`find_free_extent()` searches block groups by RAID index and retry loop phase. It handles:
- Hints and first logical byte.
- Cached and uncached block groups.
- Free-space cache errors.
- Block-group size-class preference.
- Clustered allocation for normal filesystems.
- Sequential allocation for zoned filesystems.
- Chunk allocation fallback.
- Fragmentation reporting through `ins->offset` on `-ENOSPC`.

Loop phases:
- `LOOP_CACHING_NOWAIT`
- `LOOP_CACHING_WAIT`
- `LOOP_UNSET_SIZE_CLASS`
- `LOOP_ALLOC_CHUNK`
- `LOOP_WRONG_SIZE_CLASS`
- `LOOP_NO_EMPTY_SIZE`

Clustered allocation:
- Uses `fetch_cluster_info()` to select metadata or data clusters.
- `find_free_extent_clustered()` allocates from an existing or newly found cluster.
- `find_free_extent_unclustered()` searches directly and marks clusters fragmented.
- `prepare_allocation_clustered()` may disable clustering based on known max contiguous extent size.

Zoned allocation:
- `do_allocation_zoned()` only allocates sequentially from `alloc_offset`.
- It enforces dedicated tree-log and data-relocation block groups.
- It activates data block groups when required.
- It prevents normal allocations from a data-relocation block group.
- `can_allocate_chunk_zoned()` respects active-zone limits and may finish a data block group to make room.

On allocation success, reserved bytes are added to the block group and the returned key records the logical start and length.

## Reserved Extent Insertion

Once logical space is reserved, on-disk extent items are inserted later:

- `alloc_reserved_extent()` removes the range from the free-space tree and increments block-group used accounting.
- `alloc_reserved_file_extent()` inserts a data extent item with inline data/shared-data backref and optional simple-quota owner ref.
- `alloc_reserved_tree_block()` inserts a metadata/tree-block extent item, using skinny metadata when available and full tree block info otherwise.
- `btrfs_alloc_reserved_file_extent()` queues a delayed data ref for a newly allocated file extent.
- `btrfs_free_reserved_extent()` returns an unused reservation to free space and reserved-byte accounting.

## Tree Block Allocation

`btrfs_alloc_tree_block()` reserves metadata space, allocates a logical extent, initializes an extent buffer, and queues the delayed tree ref unless the block belongs to the tree log.

`btrfs_init_new_buffer()`:
- Finds or creates the extent buffer.
- Sets lockdep class, level, owner, bytenr, generation, fsid, and chunk-tree UUID.
- Clears stale/zoned-zeroout state.
- Marks it dirty in the transaction dirty-page tree or the log root dirty-log tree.
- Handles tree-log double-buffered dirty log bits by `log_index`.

Relocation tree blocks are marked with `BTRFS_BLOCK_FLAG_FULL_BACKREF` and may use the relocation source root as owning root.

Debug builds include `check_eb_lock_owner()` to catch allocator reuse of an already locked tree block, which would indicate extent-tree corruption.

## Tree Block Freeing

`btrfs_free_tree_block()` queues a delayed metadata ref drop for non-tree-log blocks. If the block’s last ref is being dropped in the current transaction, it may be:
- Pinned if already written, if tree mod log users exist, or on zoned filesystems.
- Immediately returned to free space if still clean/unwritten and safe.
- Directly pinned for tree-log blocks.

`btrfs_free_extent()` is the generic public free path for metadata/data refs and special-cases tree-log extents.

## Snapshot and Subtree Drop

`btrfs_drop_snapshot()` drops an entire subvolume/root tree, including shared-subtree handling and resumable progress.

The deletion walker uses `struct walk_control` and two stages:
- `DROP_REFERENCE`: normal traversal, dropping refs to children or freeing blocks owned only by the deleted root.
- `UPDATE_BACKREF`: entered when a shared block requires full-backref conversion before dropping the root’s implicit reference.

Core walker helpers:
- `visit_node_for_delete()` decides whether a child must be visited or can be skipped/ref-dropped.
- `walk_down_proc()` checks refs/flags and performs full-backref conversion when required.
- `do_walk_down()` reads/locks child blocks, determines refs/flags, and descends or drops references.
- `maybe_drop_reference()` drops a child reference without visiting it and traces qgroup shared subtrees when needed.
- `walk_up_proc()` frees blocks after children are processed, decrements refs for leaf file extents, traces qgroup leaf items, and frees tree blocks.
- `walk_down_tree()` and `walk_up_tree()` coordinate traversal.
- `reada_walk_down()` adaptively readaheads child nodes during deletion.
- `check_ref_exists()` validates restart state when `drop_progress` was previously persisted.
- `check_next_block_uptodate()` safely reads a non-uptodate child block with parent checks.

`btrfs_drop_snapshot()` persists `drop_progress` and `drop_level` so interrupted drops can resume. It updates root items, deletes root/orphan items, releases qgroup metadata reservations, queues dropped roots, cleans up dropped-subvolume qgroups, and wakes unfinished-drop waiters.

`btrfs_drop_subtree()` is the relocation-only subtree drop helper. It receives locked parent and subtree root buffers, sets full-backref context, walks down/up, and releases the subtree.

## Simple Quota and Qgroup Integration

The file integrates quota accounting throughout:

- New data and metadata extents record `btrfs_squota_delta` increments.
- Final ref drops record simple-quota decrements, deriving owner root from owner refs for data extents.
- Delayed ref head reservations are released through qgroup APIs.
- Snapshot deletion traces shared subtrees and leaf file extents for full qgroup accounting.
- Dropped subvolume qgroups are cleaned after a successful root drop.

## Error Handling and Integrity Checks

Common strategies:
- Return `-ENOMEM`, `-ENOSPC`, `-EAGAIN`, `-EUCLEAN`, `-EIO`, or interruption errors as appropriate.
- Abort the transaction on extent-tree corruption or unrecoverable metadata update failure.
- Print problematic leaves and keys for backref/extent item inconsistencies.
- Use assertions for impossible internal states, such as invalid tree block ref modifiers or missing block groups in logic-only paths.
- Continue best-effort trim/discard after non-fatal per-device/per-block-group errors.

## Important Invariants

- Extent item ref counts must never reach zero while the item remains present.
- Tree-block refs are single-count refs; data refs can carry counts.
- Inline backrefs are ordered consistently with keyed backref ordering.
- Skinny metadata lookups must fall back to old full extent items for converted filesystems.
- Freed extents are pinned until transaction commit unless proven safe for immediate reuse.
- Tree-log blocks do not enter the normal extent allocation tree.
- Delayed ref head `must_insert_reserved` ownership must be cleared only when all reservations will be released or pinned.
- Snapshot deletion cannot allow concurrent fs-tree mutation while walking and dropping refs.
- Full-backref conversion is required before dropping implicit refs from shared blocks in cases where descendants still need correct ownership.
- Zoned allocation is sequential and must isolate tree-log/data-relocation block groups.

## External Dependencies

This file depends heavily on Btrfs internals:
- B-tree operations from `ctree.h`, `disk-io.h`, `locking.h`, and accessors.
- Delayed refs and transactions from `transaction.h`.
- Block-group/free-space APIs from `block-group.h`, `free-space-cache.h`, and `free-space-tree.h`.
- Space reservations from `space-info.h` and `block-rsv.h`.
- Qgroup/simple-quota APIs from `qgroup.h`.
- Discard/zoned/device replacement from `discard.h`, `zoned.h`, `volumes.h`, and `dev-replace.h`.
- Checksums, RAID stripe tree, remap tree, relocation, tree checker, orphan handling, and ref verification helpers.
