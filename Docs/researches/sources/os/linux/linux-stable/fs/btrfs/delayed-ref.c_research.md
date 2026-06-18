# File Research: sources/os/linux/linux-stable/fs/btrfs/delayed-ref.c

This file implements delayed back-reference tracking for Btrfs extents. It queues extent refcount changes, merges compatible operations, maintains reservation accounting, tracks qgroup dirty extents, and supplies ordered ref heads to extent-tree processing.

Purpose:
- Avoid deep recursive extent-tree updates while modifying btrees.
- Batch and merge frequent backref updates.
- Keep accurate delayed ref, csum deletion, qgroup, and reserved extent accounting until transaction commit.

Slab caches:
- `btrfs_delayed_ref_head_cachep`
- `btrfs_delayed_ref_node_cachep`
- `btrfs_delayed_extent_op_cachep`

Reservation management:
- `btrfs_check_space_for_delayed_refs()` compares delayed-ref reserve size against delayed reserve plus global reserve.
- `btrfs_delayed_refs_rsv_release()` releases metadata reservation for delayed refs and pending csum deletions.
- `btrfs_update_delayed_refs_rsv()` transfers bytes from a transaction-local delayed reserve into the filesystem delayed-ref reserve.
- `btrfs_inc/dec_delayed_refs_rsv_bg_inserts()` account block group item insertions.
- `btrfs_inc/dec_delayed_refs_rsv_bg_updates()` account block group item updates.
- `btrfs_zoned_cap_metadata_reservation()` caps delayed-ref reservation on zoned filesystems.
- `btrfs_delayed_refs_rsv_refill()` reserves metadata bytes up to one delayed-ref item unit and handles races with other refillers.

Ref comparison and merging:
- `comp_data_refs()` compares data refs by objectid and file-relative offset.
- `comp_refs()` compares ref type, parent/ref root, data ref payload, and optionally sequence.
- `tree_insert()` inserts into a delayed-ref head rbtree.
- `merge_ref()` merges adjacent equivalent refs, canceling opposite add/drop operations when possible.
- `btrfs_merge_delayed_refs()` merges metadata refs that are not held back by tree mod log sequence requirements.
- `btrfs_check_delayed_seq()` detects refs that must wait behind the current tree mod log lowest sequence.

Ref head selection:
- Delayed ref heads are tracked in `delayed_refs->head_refs` xarray indexed by bytenr shifted by sectorsize bits.
- `btrfs_select_ref_head()` selects the next non-processing head, marks it processing, updates ready counters and scan start, then locks the head mutex.
- `btrfs_unselect_ref_head()` clears processing and requeues readiness.
- `btrfs_delete_ref_head()` removes a head from the xarray and updates counters.
- `btrfs_select_delayed_ref()` prefers add refs from `ref_add_list` before drops to avoid deleting an extent item before pending additions are applied.

Adding refs:
- `init_delayed_ref_head()` initializes aggregate head state, ref_mod, reserved bytes, extent-op state, data/system flags, metadata level, and qgroup record fields.
- `add_delayed_ref_head()` inserts or updates a head, handles qgroup trace record insertion, pending csum accounting, and head counters.
- `init_delayed_ref_common()` initializes an individual delayed ref node from `struct btrfs_ref`.
- `btrfs_init_tree_ref()` initializes metadata ref details and qgroup skip policy.
- `btrfs_init_data_ref()` initializes data ref details and qgroup skip policy.
- `add_delayed_ref()` allocates node/head/qgroup record, reserves xarray slots, inserts the head and node under lock, updates delayed-ref reserve, emits tracepoints, and posts qgroup trace records.
- `btrfs_add_delayed_tree_ref()` wraps metadata refs.
- `btrfs_add_delayed_data_ref()` wraps data refs.
- `btrfs_add_delayed_extent_op()` queues a head-only extent operation update.

Lookup helpers:
- `btrfs_find_delayed_ref_head()` loads a head by bytenr under delayed-root lock.
- `btrfs_find_delayed_tree_ref()` searches a head for an add ref matching a metadata root/parent pair.

Cleanup:
- `btrfs_put_delayed_ref()` releases node refcounts.
- `btrfs_destroy_delayed_refs()` destroys all remaining delayed refs during transaction abort/cleanup. It drops nodes, frees extent ops, deletes heads, handles must-insert-reserved pinning, cleans accounting, and destroys qgroup extent records.
- `btrfs_delayed_ref_init()` creates caches.
- `btrfs_delayed_ref_exit()` destroys caches.

Concurrency:
- `delayed_refs->lock` protects xarrays, head counters, pending csums, flags, and scan position.
- Each head has a mutex for processing serialization.
- Each head also has a spinlock protecting its rbtree and add-list.
- Locking carefully handles the race where a head disappears while waiting for its mutex.

Role in Btrfs:
This file is core transaction infrastructure for extent reference consistency. It ensures COW extent allocation/free/reference updates can be queued safely, merged, accounted, and replayed against the extent tree without corrupting refcounts or exhausting metadata reserves unexpectedly.
