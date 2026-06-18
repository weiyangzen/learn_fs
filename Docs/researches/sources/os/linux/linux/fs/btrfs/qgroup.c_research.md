# File Research: sources/os/linux/linux/fs/btrfs/qgroup.c

This file implements Btrfs quota groups, including full qgroup accounting, simple quota accounting, config loading, qgroup relations, quota enable/disable, rescans, reservations, delayed extent accounting, and relocation swap handling.

Modes:
- `btrfs_qgroup_mode()` returns disabled, full, or simple mode.
- `btrfs_qgroup_enabled()` and `btrfs_qgroup_full_accounting()` are mode predicates.
- Full accounting tracks referenced/exclusive bytes through backref walks.
- Simple quota mode tracks ownership deltas against root ownership and propagates through parent qgroups.

In-memory state:
- Qgroups live in `fs_info->qgroup_tree`, keyed by qgroup ID.
- Relation lists model parent/member links between qgroups.
- Dirty qgroups are queued on `fs_info->dirty_qgroups` and written by `btrfs_run_qgroups()`.
- Iterator lists prevent duplicate propagation through parent graphs.

On-disk config:
- `btrfs_read_qgroup_config()` reads the quota tree at mount in two passes: status/info/limit items first, relation items second.
- Generation or config mismatches mark full qgroups inconsistent.
- Simple mode reads `qgroup_enable_gen`.
- `add_qgroup_item()`, `del_qgroup_item()`, relation item helpers, and update helpers maintain quota-tree records.

Enable/disable:
- `btrfs_quota_enable()` creates the quota tree, status item, qgroup records for existing roots, and the fs tree qgroup.
- Full mode starts inconsistent and queues a rescan; simple mode sets the simple-quota incompat flag and enable generation.
- `btrfs_quota_disable()` cancels/waits for rescans, flushes outstanding reservations, clears runtime state, deletes quota-tree contents, deletes the quota root, and frees qgroup config.
- Several paths deliberately drop `qgroup_ioctl_lock` around transaction start/commit to avoid lock inversions.

Relation and lifecycle operations:
- `btrfs_add_qgroup_relation()` validates qgroup levels, creates both relation items, adds in-memory relation state, and attempts quick accounting propagation.
- `btrfs_del_qgroup_relation()` removes relation items and in-memory links.
- `btrfs_create_qgroup()` creates a qgroup item and sysfs entry.
- `btrfs_remove_qgroup()` verifies deletability, removes relations/items, warns on non-zero reservations, and may mark full qgroups inconsistent.
- `btrfs_qgroup_cleanup_dropped_subvolume()` removes dropped subvolume qgroups after committing current accounting.
- `btrfs_limit_qgroup()` updates referenced/exclusive and reservation limits; `(u64)-1` clears a limit.

Delayed extent tracing and accounting:
- `btrfs_qgroup_trace_extent_nolock()` records dirty extents in delayed refs’ xarray by sectorsize-shifted bytenr.
- `btrfs_qgroup_trace_extent_post()` populates old roots using commit-root backref walks outside spinlock context.
- `btrfs_qgroup_trace_extent()` wraps allocation, xarray reservation, insert, and post-processing.
- `btrfs_qgroup_trace_leaf_items()` traces non-inline file extents in a leaf.
- `btrfs_qgroup_account_extents()` walks dirty extent records at transaction commit, finds new roots, accounts deltas, frees old root lists, releases data reservations, erases xarray records, and frees memory.
- `btrfs_qgroup_destroy_extent_records()` cleans dirty extent records when a transaction is destroyed.

Full accounting counters:
- `qgroup_update_refcnt()` propagates old/new root reference counts through parent qgroups.
- `qgroup_update_counters()` updates referenced and exclusive counters from old/new root cardinality.
- `btrfs_qgroup_account_extent()` coordinates refcount updates, skips non-fs-tree roots, handles rescan overlap, bumps `qgroup_seq`, and frees root lists.

Subtree tracing:
- `btrfs_qgroup_trace_subtree()` traces a subtree for snapshot drop or relocation unless the configured drop-subtree threshold would make it too expensive, in which case full qgroups are marked inconsistent.
- `qgroup_trace_subtree_swap()` and helpers trace swapped relocation/subvolume subtrees using generation-aware traversal.
- Leaf tracing also records file extent items when requested.

Rescan:
- `btrfs_qgroup_rescan()` initializes a full qgroup rescan, commits current work, zeroes counters, and queues the worker.
- `qgroup_rescan_leaf()` scans extent-tree leaves from progress, clones the leaf before accounting, and accounts each extent against current roots.
- `btrfs_qgroup_rescan_worker()` loops transactions until complete, stopped, cancelled, or errored, then updates status and completion state.
- `btrfs_qgroup_rescan_resume()` restarts queued rescans at mount.
- `btrfs_qgroup_wait_for_completion()` waits for the worker.

Inheritance:
- `btrfs_qgroup_check_inherit()` validates ioctl inheritance structures and rejects legacy ref/excl copy behavior.
- `qgroup_auto_inherit()` builds simple-quota inheritance from the source root’s parent qgroups.
- `qgroup_snapshot_quick_inherit()` avoids full rescans for a narrow full-accounting snapshot case.
- `btrfs_qgroup_inherit()` creates destination qgroups, relation items, inherited limits, and initial counters for subvolume/snapshot creation.

Reservation handling:
- `qgroup_reserve()` enforces limits and records reservations through all parent qgroups.
- `btrfs_qgroup_reserve_data()` marks inode `io_tree` ranges with `EXTENT_QGROUP_RESERVED`, reserves qgroup data bytes, and retries after flushing on quota exhaustion.
- `btrfs_qgroup_release_data()` clears range reservation bits after data reaches disk without freeing qgroup reservation counters.
- `btrfs_qgroup_free_data()` clears range reservation bits and frees qgroup counters for invalidation/error paths.
- Metadata reservation APIs manage `META_PREALLOC` and `META_PERTRANS` reservations and root-side counters to avoid disable/enable underflows.
- `btrfs_qgroup_check_reserved_leak()` detects and releases leaked per-inode data reservation bits.

Simple quota:
- `btrfs_record_squota_delta()` applies simple quota deltas for extents whose generation is after `qgroup_enable_gen`, propagating referenced/exclusive changes through parent qgroups.
- Simple quota parent usage consistency is checked by `squota_check_parent_usage()`.

Relocation swapped blocks:
- `btrfs_qgroup_init_swapped_blocks()` initializes per-root swapped-block rb-trees.
- `btrfs_qgroup_add_swapped_blocks()` records delayed subtree tracing metadata during balance relocation swaps.
- `btrfs_qgroup_trace_subtree_after_cow()` detects COW of a recorded swapped subtree, reads the relocation counterpart, traces the swap, and removes the record.
- `btrfs_qgroup_clean_swapped_blocks()` drops stale records at transaction commit.

Risk areas:
- Lock ordering around `qgroup_ioctl_lock`, transaction handles, rescan locks, and extent-buffer locks is central to correctness.
- Full accounting depends on expensive backref walks and marks qgroups inconsistent when accounting cannot be trusted.
- Reservation underflow is guarded with warnings and root-side metadata reservation tracking.
- Rescan/live accounting overlap is handled through progress checks and runtime flags.
