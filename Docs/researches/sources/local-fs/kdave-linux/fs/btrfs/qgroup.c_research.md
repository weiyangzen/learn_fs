# File Research: sources/local-fs/kdave-linux/fs/btrfs/qgroup.c

## Purpose

Implements Btrfs quota groups, including full qgroup accounting, simple quotas, reservation tracking, qgroup relations, qgroup rescan, snapshot inheritance, delayed extent tracing, and balance subtree-swap accounting.

## Modes

- `BTRFS_QGROUP_MODE_DISABLED`: quotas off.
- `BTRFS_QGROUP_MODE_FULL`: classic qgroups with referenced/exclusive accounting from backrefs.
- `BTRFS_QGROUP_MODE_SIMPLE`: simple quota mode using owner-generation deltas and no full rescan worker.

Mode helpers:
- `btrfs_qgroup_mode()`
- `btrfs_qgroup_enabled()`
- `btrfs_qgroup_full_accounting()`

## In-Memory Model

Qgroups are stored in `fs_info->qgroup_tree` by qgroup id. Relations are stored as `struct btrfs_qgroup_list` links:
- `groups`: parents a qgroup belongs to.
- `members`: children of a parent qgroup.
- `dirty`: qgroups needing on-disk info/limit updates.
- iterator lists support breadth-style parent traversal during accounting.

Reservation categories:
- data
- metadata per-transaction
- metadata preallocation

Reservation helpers add/release per-type byte counts and propagate changes through parent qgroups.

## Config Load and Free

`btrfs_read_qgroup_config()` reads the quota tree during mount:
- Reads status, qgroup info, and limit items.
- Builds qgroup rb-tree entries.
- Reads relation items in a second pass.
- Sets quota enabled state and resumes pending rescans.
- Marks full qgroups inconsistent on generation/config mismatch.
- Reads simple quota enable generation when `SIMPLE_QUOTA` is active.

`btrfs_free_qgroup_config()` removes sysfs entries and frees qgroups/relations.

`btrfs_check_quota_leak()` reports unreleased reservation values at unmount.

## Enable and Disable

`btrfs_quota_enable()`:
- Requires `subvol_sem` write lock.
- Rejects extent tree v2.
- Creates quota tree and status item.
- Creates qgroup info/limit items for existing subvolumes and fs tree.
- Supports simple quota enable, setting `SIMPLE_QUOTA`, `qgroup_enable_gen`, and `BTRFS_FS_SQUOTA_ENABLING`.
- For full qgroups, marks initial state inconsistent and queues a rescan.

`btrfs_quota_disable()`:
- Requires `subvol_sem` write lock and `cleaner_mutex`.
- Stops rescan, flushes delayed allocation/ordered extents, commits outstanding reservations, removes quota root, clears mode flags, frees config, and commits.

## Qgroup CRUD and Relations

- `btrfs_create_qgroup()`: creates on-disk info/limit items, adds rb-tree and sysfs entry.
- `btrfs_remove_qgroup()`: verifies the qgroup can be deleted, removes relation/item state, warns on nonzero counters or reservations, removes sysfs entry.
- `btrfs_add_qgroup_relation()`: creates bidirectional relation items and in-memory link.
- `btrfs_del_qgroup_relation()`: removes bidirectional relation items and in-memory link.
- `btrfs_limit_qgroup()`: updates limit fields, with `-1` meaning clear the selected limit.

Fast relation accounting is attempted when a child has only exclusive references. Otherwise full qgroups are marked inconsistent.

Simple quota parent usage is checked by summing member usage and warning on mismatch.

## Dirty Extent Tracing and Full Accounting

Full qgroups account by tracing extents whose ownership/reference set changes.

Key entry points:
- `btrfs_qgroup_trace_extent_nolock()`: stores a dirty extent record in the delayed-ref xarray.
- `btrfs_qgroup_trace_extent_post()`: after lock release, finds old roots from commit roots.
- `btrfs_qgroup_trace_extent()`: allocates and inserts the record, then does post-processing.
- `btrfs_qgroup_trace_leaf_items()`: traces file extents referenced from a leaf.
- `btrfs_qgroup_account_extents()`: at transaction commit, finds new roots for each dirty extent and updates qgroups.
- `btrfs_qgroup_account_extent()`: updates rfer/excl counters from old/new root sets.

Accounting logic:
- `qgroup_update_refcnt()` walks root qgroups and parents to accumulate old/new reference counts.
- `qgroup_update_counters()` adjusts referenced and exclusive counters based on transitions between no refs, shared refs, and exclusive refs.
- Non-filesystem roots are ignored by `maybe_fs_roots()`.
- `qgroup_to_skip` can remove a root from old/new root sets before accounting.

## Subtree and Balance Swap Handling

Subtree tracing is used for snapshot deletion and relocation/balance cases:
- `btrfs_qgroup_trace_subtree()` walks a subtree, traces metadata blocks and file extents, and may mark qgroups inconsistent if the subtree level exceeds the configured threshold.
- `qgroup_trace_subtree_swap()` and helpers compare old/new swapped subtrees and trace corresponding blocks.
- `btrfs_qgroup_add_swapped_blocks()` records delayed subtree-swap accounting entries during relocation.
- `btrfs_qgroup_trace_subtree_after_cow()` detects COW of a swapped subtree root and performs deferred accounting.
- `btrfs_qgroup_clean_swapped_blocks()` drops deferred records at transaction commit.

This is an optimization for balance: if swapped subtrees remain structurally unchanged, the expensive scan can be skipped.

## Snapshot/Subvolume Inheritance

- `btrfs_qgroup_check_inherit()` validates inherit structures and rejects legacy ref/excl copy modes.
- `btrfs_qgroup_inherit()` creates the destination qgroup, applies inherited limits/relations, copies source accounting for snapshots in full mode, and may mark qgroups inconsistent if a rescan is required.
- Simple quota mode can auto-inherit parent qgroups from the inode root with `qgroup_auto_inherit()`.
- `qgroup_snapshot_quick_inherit()` can avoid rescan for a narrow full-qgroup case where parent ownership remains exclusive.

## Reservations

Data reservation:
- `btrfs_qgroup_reserve_data()` marks inode io_tree ranges with `EXTENT_QGROUP_RESERVED` and reserves quota bytes.
- On `-EDQUOT`, it tries flushing delalloc, ordered extents, delayed iputs, and a transaction commit, then retries.
- `btrfs_qgroup_release_data()` clears io_tree reservation bits after data reaches disk but does not free qgroup reservation bytes.
- `btrfs_qgroup_free_data()` clears bits and frees reservation bytes.

Metadata reservation:
- `btrfs_qgroup_reserve_meta_prealloc()`
- `btrfs_qgroup_free_meta_prealloc()`
- `btrfs_qgroup_convert_reserved_meta()`
- `btrfs_qgroup_free_meta_all_pertrans()`

Root-local metadata reservation counters prevent underflow when quotas are toggled around outstanding reservations.

`btrfs_qgroup_check_reserved_leak()` detects and frees leaked inode data reservations at inode destruction.

## Rescan

Full qgroup rescan:
- `btrfs_qgroup_rescan()` initializes rescan, commits current transaction, zeroes existing counters, and queues worker.
- `btrfs_qgroup_rescan_worker()` scans extent tree leaves through commit roots and accounts each extent.
- `qgroup_rescan_leaf()` clones a leaf under the rescan lock, then performs backref walking outside the lock.
- Rescan stops on filesystem closing, remounting, quota disable, or cancel flag.
- Completion can be waited through `btrfs_qgroup_wait_for_completion()`.
- `btrfs_qgroup_rescan_resume()` queues pending mount-time rescan.

Simple quota mode rejects rescan initialization.

## Simple Quota Deltas

`btrfs_record_squota_delta()` handles simple quota accounting:
- Ignores non-fs trees.
- Ignores extents older than `qgroup_enable_gen`.
- Updates level-0 qgroup and parent qgroups directly.
- Assumes simple quota `excl == rfer`.
- Warns and clamps on underflow.

## Error Handling and Consistency

`qgroup_mark_inconsistent()` marks full qgroups inconsistent, cancels rescan, and disables accounting through runtime flags. It is intentionally a no-op for simple quota mode.

Common consistency triggers:
- quota status generation mismatch
- qgroup config inconsistencies
- xarray insertion failure
- backref walk/accounting failure
- qgroup item update errors
- subtree threshold exceeded
- impossible/mismatched swapped-block records

## Role in the System

This is the central implementation of Btrfs quota behavior. It ties together on-disk quota-tree metadata, transaction commit accounting, delayed refs, backref walking, reservation enforcement, snapshot inheritance, sysfs qgroup visibility, and simple quota updates.
