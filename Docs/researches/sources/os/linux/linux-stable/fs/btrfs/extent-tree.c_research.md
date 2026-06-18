# File Research: sources/os/linux/linux-stable/fs/btrfs/extent-tree.c

## Role

`extent-tree.c` is the central Btrfs implementation for extent ownership, extent reference accounting, physical/logical extent allocation, block-group pinning/unpinning, discard/trim, tree block allocation/freeing, and snapshot/subtree deletion. It sits below higher-level inode, file, relocation, log replay, transaction, qgroup, free-space, RAID stripe tree, and zoned-device code, and is responsible for keeping extent-tree items, backreferences, free-space records, and block-group accounting consistent.

The file implements both metadata and data extent lifecycles. Data extents are tracked by `BTRFS_EXTENT_ITEM_KEY` plus data backrefs; metadata can use old "fat" extent items or `SKINNY_METADATA` `BTRFS_METADATA_ITEM_KEY`s. The code has many compatibility paths for old extent formats, mixed block groups, simple quotas, relocation roots, tree-log roots, zoned filesystems, async/sync discard, and remapped block groups.

## Main Responsibilities

- Look up extent items and merge committed extent-tree state with pending delayed-reference state (`btrfs_lookup_data_extent()`, `btrfs_lookup_extent_info()`).
- Validate, locate, insert, update, and remove inline and keyed backreferences for data and tree blocks.
- Queue and run delayed refs, including extent-item creation, ref-count changes, last-ref frees, qgroup/simple-quota accounting, csum deletion, RAID extent deletion, free-space-tree updates, and transaction abort handling.
- Allocate physical extents from block groups with clustered allocation on regular filesystems and sequential allocation on zoned filesystems.
- Reserve, free, pin, unpin, and commit extents while maintaining block-group and `space_info` counters.
- Allocate and initialize new tree blocks and create their delayed extent refs.
- Free tree blocks, file extents, snapshots, and relocation subtrees while preserving Btrfs backreference rules.
- Issue discard/TRIM across mapped stripes, block groups, and device unallocated space.
- Finalize block-group remapping by discarding remapped ranges and removing now-unused remapped chunks/device extents.

## Backreference Model

The long in-file comment documents the Btrfs backreference rules:

- Backrefs distinguish all holders of an extent, support corruption/owner discovery, and enable shrinking/relocation.
- Implicit tree backrefs identify owner root and lowest key/level for non-shared owner-tree pointers.
- Full tree backrefs identify the parent block address, used when a tree block is not referenced by its owner tree or when shared state requires full backrefs.
- Data backrefs can be implicit `BTRFS_EXTENT_DATA_REF_KEY` entries keyed by a hash of `(root, owner inode, file offset)`, or full/shared `BTRFS_SHARED_DATA_REF_KEY` entries keyed by parent.
- Tree block refs are `BTRFS_TREE_BLOCK_REF_KEY` or `BTRFS_SHARED_BLOCK_REF_KEY`.
- Simple quotas may add an inline `BTRFS_EXTENT_OWNER_REF_KEY` before the real backrefs to record the allocating root.

Important helpers:

- `btrfs_get_extent_inline_ref_type()` validates inline ref type against expected data/tree context and prints the leaf on corruption.
- `hash_extent_data_ref()` builds the 64-bit data-ref key hash from CRC32C pieces.
- `match_extent_data_ref()` compares the full `(root, objectid, offset)` payload because hash collisions are possible.
- `extent_ref_type()` selects data/tree and shared/implicit ref key type from `parent` and `owner`.
- `lookup_inline_extent_backref()` searches an extent item's inline refs in their on-disk order, supports skinny metadata fallback to fat extent items, can reserve item growth for insertion, skips simple-quota owner refs, and returns `-EAGAIN` when a keyed ref is needed instead of another inline ref.
- `setup_inline_extent_backref()` and `update_inline_extent_backref()` grow/shrink the extent item, shift inline ref bytes, update aggregate extent refs, and apply delayed extent ops.
- `lookup_extent_backref()` first tries inline refs, then keyed tree/data refs.
- `insert_extent_data_ref()`, `remove_extent_data_ref()`, `insert_tree_block_ref()`, and `lookup_tree_block_ref()` handle non-inline backref items.

## Delayed References

Public entry points such as `btrfs_inc_extent_ref()`, `btrfs_free_extent()`, `btrfs_inc_ref()`, `btrfs_dec_ref()`, `btrfs_alloc_reserved_file_extent()`, and `btrfs_alloc_tree_block()` usually queue delayed refs instead of mutating the extent tree immediately. Running delayed refs is the main mutation pipeline:

- `run_delayed_data_ref()` handles data add/drop nodes. `BTRFS_ADD_DELAYED_REF` either inserts a newly reserved extent item or increments refs on an existing extent; `BTRFS_DROP_DELAYED_REF` frees refs through `__btrfs_free_extent()`.
- `run_delayed_tree_ref()` handles metadata add/drop nodes, enforces one ref per tree-block ref node, supports remap-tree drops, and records simple-quota deltas for new tree blocks.
- `run_one_delayed_ref()` dispatches by ref key type and pins reserved extents on errors when necessary.
- `btrfs_run_delayed_refs_for_head()` selects nodes from a delayed-ref head, merges refs, updates `head->ref_mod`, clears `must_insert_reserved` at the ownership handoff point, runs the ref, releases delayed-ref reservation bytes, and frees the delayed extent op.
- `cleanup_ref_head()` runs any leftover extent op, removes empty heads, pins abandoned reserved extents, deletes csums for abandoned new data extents, releases accounting, unlocks the head, and drops the head ref.
- `__btrfs_run_delayed_refs()` repeatedly selects heads until requested byte work is processed or all current heads are handled.
- `btrfs_run_delayed_refs()` wraps the loop, skips work during free-space-tree creation, aborts transactions on hard errors, and for `U64_MAX` keeps looping through pending block-group creation and newly added refs.

Delayed extent ops carry tree-block flag/key updates. `__run_delayed_extent_op()` sets extent flags and, for fat metadata items, stores tree block key/level information. `cleanup_extent_op()` discards ops that are superseded by inserting the reserved extent item.

## Freeing Extents

`__btrfs_free_extent()` is the authoritative on-disk ref drop routine. It:

- Locates the matching inline or keyed backref.
- Locates the owning `EXTENT_ITEM` or `METADATA_ITEM`, with quick neighbor lookup and slow fallback.
- Validates item size, metadata owner/level, and ref counts.
- Decrements aggregate refs and the matching backref when refs remain.
- Deletes the extent item and possible adjacent keyed shared ref when the last ref is dropped.
- For last data refs, recovers the simple-quota owner root from the inline owner ref if present.
- Calls `do_free_extent_accounting()` to remove remap-tree records, delete csums, delete RAID stripe tree extent records, record simple-quota delta, add free-space-tree entries, and update block-group usage.

`check_ref_cleanup()` opportunistically removes delayed-ref heads for just-freed blocks when no pending refs remain and reports whether an uninserted reserved extent needs further handling.

`btrfs_free_tree_block()` queues a delayed tree-ref drop except for tree-log blocks, then decides whether the physical tree block can be returned immediately or must be pinned. It pins written blocks, blocks visible to tree-mod-log users, and zoned blocks; otherwise it can return newly allocated, unwritten tree blocks directly to free space and free reserved bytes.

## Extent Allocation

`btrfs_reserve_extent()` is the public allocator. It chooses an allocation profile with `get_alloc_profile_by_root()`, fills `struct find_free_extent_ctl`, and calls `find_free_extent()`. If `-ENOSPC` reports a smaller largest hole and `num_bytes > min_alloc_size`, it retries with a smaller rounded size down to `min_alloc_size`.

`find_free_extent()`:

- Selects `space_info` by block-group profile, with zoned sub-space-info overrides for tree-log and data-relocation allocations.
- Chooses `BTRFS_EXTENT_ALLOC_CLUSTERED` for normal filesystems or `BTRFS_EXTENT_ALLOC_ZONED` for zoned filesystems.
- Uses hints from allocation clusters, active zoned block groups, dedicated tree-log block group, or dedicated data-relocation block group.
- Iterates block groups by RAID index under `groups_sem`, skipping readonly/remapped/incompatible block groups.
- Starts free-space caching for uncached groups and may wait once for cache progress in later loops.
- Applies size-class filtering until relaxed by later allocation loops.
- Allocates from a cluster, unclustered free space, or a zoned block group's sequential `alloc_offset`.
- Validates stripe alignment and block-group bounds, returns unused fragments, reserves bytes in the block group, increments reservation counters, and returns the found logical address in `ins`.
- Runs retry phases: no-wait caching, wait on caching, allow unset size class, force chunk allocation, ignore wrong size class, and finally drop empty-size/cluster hints.

Clustered allocation uses `btrfs_find_space_cluster()` and `btrfs_alloc_from_cluster()` via `find_free_extent_clustered()`, falling back to unclustered allocation when fragmented. `find_free_extent_unclustered()` marks the cluster fragmented and calls `btrfs_find_space_for_alloc()`.

Zoned allocation in `do_allocation_zoned()` is sequential-only. It:

- Enforces dedicated tree-log and data-relocation block groups.
- Activates data block groups before use.
- Checks zone capacity and advances `block_group->alloc_offset`.
- Updates the free-space control's available bytes.
- Sets `fs_info->treelog_bg` or `fs_info->data_reloc_bg` and the `BLOCK_GROUP_FLAG_ZONED_DATA_RELOC` runtime flag when needed.

`can_allocate_chunk_zoned()` understands max active zone limits, may finish one active data block group to make room, and can return `-EAGAIN` or `-ENOSPC` when creating another chunk would not help.

## Reserved Extent and Tree Block Creation

`alloc_reserved_extent()` removes an already reserved range from the free-space tree and updates block-group used bytes.

`alloc_reserved_file_extent()` inserts the data extent item, optional simple-quota owner inline ref, and the first data/shared data inline ref, then calls `alloc_reserved_extent()`.

`alloc_reserved_tree_block()` inserts a metadata extent item unless it belongs to the remap tree, supports skinny and fat metadata formats, records tree-block info for fat metadata, writes the first tree/shared block inline ref, then calls `alloc_reserved_extent()`.

`btrfs_alloc_reserved_file_extent()` builds a delayed data ref for an already-reserved file extent. For data relocation roots it records the source fs root as the owning root.

`btrfs_alloc_logged_file_extent()` is used by log replay. It excludes the logged range from free-space cache when needed, temporarily accounts it as reserved, inserts the reserved file extent, pins on failure, and records a simple-quota delta.

`btrfs_alloc_tree_block()` uses a block reservation, reserves a physical extent, initializes a new `extent_buffer`, and queues a delayed tree extent ref unless the target is the tree-log root. Relocation tree blocks are marked `BTRFS_BLOCK_FLAG_FULL_BACKREF` and use the relocation source root as the owning root.

`btrfs_init_new_buffer()` creates/fetches an extent buffer, validates debug lock ownership, sets lockdep class, locks it, clears stale/zoned-zeroout state, zeros the header, sets header fields, writes fs UUIDs, and marks either dirty transaction pages or dirty log pages.

## Pinning, Commit, Remapping, Discard, and Trim

Pinning:

- `pin_down_extent()` moves a range into transaction pinned extents, adjusts block-group pinned/reserved counters, adjusts `space_info`, and marks the range dirty in `transaction->pinned_extents`.
- `btrfs_pin_extent()` pins a reserved range by lookup.
- `btrfs_pin_extent_for_log_replay()` fully caches a block group, pins the log replay tree block without consuming reserved bytes, and removes it from free-space cache.
- `btrfs_free_reserved_extent()` returns a reserved range to free space and frees reserved bytes.
- `btrfs_pin_reserved_extent()` pins a reserved extent buffer range.
- `unpin_extent_range()` is used at commit or error handling to drop pinned accounting, optionally return free space, clear cluster fragmentation after enough unpinning, account readonly/zoned-unusable/free bytes, and process block-group boundaries.
- `btrfs_finish_extent_commit()` discards pinned ranges for sync discard, clears pinned dirty state, returns space, schedules async discard, discards deleted block groups, unfreezes and drops them, and returns the first unpin error.
- `btrfs_error_unpin_extent_range()` unpins without returning the space, for error contexts.

Remapping:

- `btrfs_complete_bg_remapping()` verifies identity remap is gone, marks the chunk map as having no stripes for device-extent removal, and moves unused remapped block groups to the unused state.
- `btrfs_handle_fully_remapped_bgs()` drains `fully_remapped_bgs`, discards each range without remap translation, completes remapping, and drops block-group refs.
- `drop_remap_tree_ref()` removes remapped extents from the free-space tree and block-group accounting.

Discard and trim:

- `btrfs_issue_discard()` aligns ranges to sectors, skips all superblock mirror locations, chunks large discards by `BTRFS_MAX_DISCARD_CHUNK_SIZE`, tolerates `-EOPNOTSUPP`, and stops on trim interruption.
- `do_discard_extent()` handles zoned zone reset, regular block-device discard, and device replace target discard/reset.
- `btrfs_discard_extent()` maps a logical range to discard stripes, blocks device replace races with the bio counter, skips missing/non-writeable devices, and sums discarded bytes.
- `btrfs_trim_fs()` first trims free ranges inside block groups, then trims unallocated device ranges.
- `btrfs_trim_free_extents_throttle()` finds clear device allocation-state ranges, skips reserved device space, issues discard up to `BTRFS_MAX_TRIM_LENGTH`, marks `CHUNK_TRIMMED`, throttles with `-EAGAIN`, and honors signals.
- `btrfs_trim_free_extents()` walks devices in UUID order while holding the device list as needed, resumes throttled devices by position, skips missing devices, records per-device failures, and lets devices added earlier in UUID order be skipped for this trim run.

## Cross-Reference Checks

`btrfs_cross_ref_exist()` is a fast "no false negatives" shared-extent check for write paths. It combines:

- `check_committed_ref()`, which searches the committed extent tree for a single inline data ref matching `(root, inode, offset)` and treats non-inline refs, shared refs, extra inline refs, mismatches, or missing owner details as shared/positive.
- `check_delayed_ref()`, which locks the relevant delayed-ref head while holding the extent leaf and scans pending refs for shared or mismatching refs.

The function can return false positives to avoid expensive full cross-reference resolution, but should not report unshared when another committed or delayed reference exists.

## Snapshot and Subtree Deletion

The `walk_control` state machine drives snapshot deletion:

- `DROP_REFERENCE`: traverse blocks owned by the root being deleted, drop references to children that do not need visiting, and free blocks once children are processed.
- `UPDATE_BACKREF`: entered when a shared block must be walked to convert child refs to full backrefs before dropping the root's normal ref.

Key helpers:

- `visit_node_for_delete()` decides whether to read/walk a child block or just drop the current reference based on ref count, `FULL_BACKREF`, generation compared to root origin generation, update-ref mode, and stored progress.
- `reada_walk_down()` adaptively readaheads children likely to be visited.
- `walk_down_proc()` looks up extent info when needed, stops descent for shared blocks in `DROP_REFERENCE`, and in `UPDATE_BACKREF` performs the conversion dance: increment full refs, drop implicit refs, and set `BTRFS_BLOCK_FLAG_FULL_BACKREF`.
- `check_ref_exists()` verifies a root ref exists in committed or delayed refs when restarting from drop progress.
- `check_next_block_uptodate()` unlocks, reads, validates parent check, and relocks a child block if it is not uptodate.
- `maybe_drop_reference()` drops a child ref without walking it, handles qgroup subtree tracing for shared subtrees, and updates drop progress.
- `do_walk_down()` obtains child extent info, decides whether to descend, switches to `UPDATE_BACKREF` for shared blocks, or drops references when safe.
- `walk_up_proc()` decrements child data/tree refs for leaves, clears dirty state, frees tree blocks, and transitions back from `UPDATE_BACKREF`.
- `walk_down_tree()` and `walk_up_tree()` implement the iterative traversal without recursion.

`btrfs_drop_snapshot()` starts or joins a transaction, runs delayed inode items, marks the root deleting, resumes from `drop_progress` if present, walks the tree while periodically updating root drop progress and ending/restarting transactions, deletes the root item and orphan item, frees qgroup metadata reservations, moves the dropped root to the dropped-root list or releases it, cleans qgroup state, wakes unfinished-drop waiters, and requeues unfinished non-relocation drops as dead roots.

`btrfs_drop_subtree()` is the relocation-only variant for a subtree below a known parent. It prepares a path with parent and child locked, forces parent full-backref state in `walk_control`, keeps locks, and walks/free refs until the subtree is dropped.

## Quotas, Simple Quotas, and Accounting

The file interacts with classic qgroups and simple quotas:

- New data/tree extents record simple-quota deltas through `btrfs_record_squota_delta()`.
- Newly inserted data extent items may contain `BTRFS_EXTENT_OWNER_REF_KEY` with the original owning root.
- `free_head_ref_squota_rsv()` releases simple-quota data reservations for delayed-ref heads whose reserved extents are abandoned or consumed.
- `btrfs_cleanup_ref_head_accounting()` releases delayed-ref reservation bytes for pending checksum deletes and frees simple-quota reservations for uninserted reserved extents.
- `btrfs_get_extent_owner_root()` parses the first inline ref to recover the original simple-quota owner root for deletion accounting.
- Snapshot deletion uses qgroup subtree and leaf tracing for shared subtrees and leaf data items, and cleans dropped-subvolume qgroup state when deletion completes.

## Concurrency and Locking

Important locking patterns:

- Delayed refs use `delayed_refs->lock`, per-head `head->lock`, and `head->mutex`. Contended head mutexes are handled by taking references, dropping outer locks/path locks, waiting, and retrying.
- Extent-tree paths are frequently kept locked while checking delayed refs to avoid races with delayed-ref flushing.
- Block-group allocation uses `space_info->groups_sem`, `block_group->lock`, `space_info->lock`, free-space-control locks, cluster `refill_lock`, and for delalloc may take `block_group->data_rwsem`.
- Zoned dedicated block groups use `fs_info->treelog_bg_lock`, `fs_info->relocation_bg_lock`, and runtime flags to prevent mixed tree-log/relocation/regular allocation.
- Discard protects against device replace/device disappearance with `btrfs_bio_counter_inc_blocked()`.
- Device trim iterates under `device_list_mutex` and uses `chunk_mutex` to avoid races with chunk allocation/release.
- Snapshot deletion intentionally unlocks parts of the tree while marking the root deleting to prevent concurrent modification of the dropping fs tree.

## Error Handling and Integrity Checks

The file aggressively treats extent-tree inconsistency as corruption:

- Missing extent/csum roots return `-EUCLEAN` and log explicit bytenr messages.
- Unexpected item sizes, zero refs, invalid inline ref types, ref underflows, invalid tree-block ref mods, mismatched owners/levels, and impossible slot layouts abort the transaction or return `-EUCLEAN`.
- The `abort_and_dump()` macro aborts with `-EUCLEAN`, prints the leaf, and logs a critical message for ref/free corruption.
- Many operations pin reserved extents on failure so space is not reused unsafely after partial failure.
- Allocation reports `space_info->max_extent_size` on `-ENOSPC` to support smaller retry decisions and diagnostics.

## External Interfaces Defined Here

Major exported functions include:

- Lookup/introspection: `btrfs_lookup_data_extent()`, `btrfs_lookup_extent_info()`, `btrfs_get_extent_inline_ref_type()`, `hash_extent_data_ref()`, `btrfs_get_extent_owner_root()`, `btrfs_cross_ref_exist()`.
- Delayed refs/ref ops: `btrfs_inc_extent_ref()`, `btrfs_free_extent()`, `btrfs_inc_ref()`, `btrfs_dec_ref()`, `btrfs_run_delayed_refs()`, `btrfs_cleanup_ref_head_accounting()`, `btrfs_set_disk_extent_flags()`.
- Allocation/free/pin: `btrfs_reserve_extent()`, `btrfs_alloc_reserved_file_extent()`, `btrfs_alloc_logged_file_extent()`, `btrfs_alloc_tree_block()`, `btrfs_free_tree_block()`, `btrfs_free_reserved_extent()`, `btrfs_pin_reserved_extent()`, `btrfs_pin_extent()`, `btrfs_pin_extent_for_log_replay()`, `btrfs_finish_extent_commit()`.
- Tree deletion: `btrfs_drop_snapshot()`, `btrfs_drop_subtree()`.
- Discard/trim/remap: `btrfs_discard_extent()`, `btrfs_trim_fs()`, `btrfs_error_unpin_extent_range()`, `btrfs_handle_fully_remapped_bgs()`, `btrfs_complete_bg_remapping()`, `btrfs_exclude_logged_extents()`.

## Dependencies

This file depends heavily on Btrfs internals:

- B-tree/search/path/extent-buffer APIs from `ctree.h`, `disk-io.h`, `locking.h`, `accessors.h`, `tree-checker.h`.
- Transaction and delayed-ref APIs from `transaction.h`, delayed inode items, root tree helpers, and orphan handling.
- Free-space and block-group APIs from `block-group.h`, `free-space-cache.h`, `free-space-tree.h`, `space-info.h`, and `block-rsv.h`.
- Device/chunk/discard/zoned/remap APIs from `volumes.h`, `discard.h`, `zoned.h`, `dev-replace.h`, and `raid-stripe-tree.h`.
- Quota APIs from `qgroup.h`.
- Relocation, ref verification, RAID56, file-item, and fs-wide state helpers.
- Linux block discard and scheduler/locking primitives.

## Research Notes

This file is not just "extent tree" code in the narrow sense. It is a cross-cutting consistency layer for Btrfs copy-on-write storage: allocation reserves space, delayed refs describe ownership changes, delayed-ref execution makes extent-tree/free-space/qgroup/csum/RAID state durable, commit unpins reusable space, and snapshot deletion drives large-scale reference drops and backref conversion. Any change here has broad blast radius across ENOSPC behavior, snapshot deletion, relocation, log replay, quotas, zoned mode, device replace, and discard.
