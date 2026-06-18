# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_dir.c

## Role

`dsl_dir.c` implements ZFS DSL directory objects: the hierarchical dataset namespace nodes that contain head datasets, children, properties, delegation metadata, clone origin metadata, quota/reservation state, usage accounting, filesystem/snapshot count limits, rename logic, and zapified extensible fields.

It is the parent accounting layer for `dsl_dataset.c` and the namespace layer used by create, destroy, rename, quota, reservation, limit, and stats operations.

## Directory Lifetime And Naming

`dsl_dir_hold_obj()` opens a dsl_dir object, validates bonus type/size, allocates and initializes `dsl_dir_t` if needed, loads encryption key object metadata and errata state, initializes properties and locks, holds the parent, resolves `dd_myname`, computes clone origin txg without recursively opening the origin dataset, installs the dbuf user, and holds the SPA for both open-to-close and instantiate-to-evict lifetime.

`dsl_dir_evict_async()` asserts no dirty/tempreserved/towrite state remains, releases the parent asynchronously, closes the SPA reference, finalizes properties, destroys the lock, and frees memory.

`dsl_dir_name()` recursively builds full dataset names, using `dd_lock` around `dd_myname`. `dsl_dir_namelen()` computes equivalent length without string concatenation. `getcomponent()` parses dataset path components and validates separators and length. `dsl_dir_hold()` resolves a full name under a specific pool, optionally returning a tail component that may be missing or be a snapshot suffix.

## Filesystem And Snapshot Limits

The header comment explains the feature-backed count/limit system. Filesystem and snapshot counts are stored as extensible ZAP properties only once the `SPA_FEATURE_FS_SS_LIMIT` feature is active. Counts are initialized lazily down a subtree when a limit is first set.

`dsl_dir_init_fs_ss_count()` recursively initializes `DD_FIELD_FILESYSTEM_COUNT` and `DD_FIELD_SNAPSHOT_COUNT`, skipping hidden `$` datasets and temporary `%` datasets/snapshots.

`dsl_dir_activate_fs_ss_limit()` runs a sync task that verifies feature support, activates the feature if needed, and initializes counts for the target subtree.

`dsl_fs_ss_limit_check()` checks whether adding filesystems or snapshots would exceed initialized limits while walking ancestors up to an optional common ancestor. It skips temporary snapshots when cred is NULL and stops at uninitialized nodes.

`dsl_fs_ss_count_adjust()` updates filesystem/snapshot counts on a dsl_dir and initialized ancestors, again skipping hidden/temp filesystem counts.

`dsl_enforce_ds_ss_limits()` decides whether limits should be enforced, not enforced, or enforced only above the current dataset based on global-zone privilege and delegated permission to modify the relevant limit property.

## Creation, Clone Detection, Stats

`dsl_dir_create_sync()` allocates a dsl_dir object, links it into the parent child ZAP or root pool directory, initializes parent object, child/property ZAPs, creation time, filesystem count, and used-breakdown flags.

`dsl_dir_is_clone()` checks for a non-origin-snap origin object. Accessors return used, compressed, quota, reservation, ratios, logical used, used-by-snap/head/refreservation/child, origin name, filesystem count, snapshot count, and last remap txg.

`dsl_dir_stats()` exports quota/reservation/logical-used, used breakdown when supported, filesystem/snapshot count, remap txg, and clone origin.

`dsl_dir_update_last_remap_txg()` zapifies the dir and monotonically updates `DD_FIELD_LAST_REMAP_TXG` through a sync task.

## Space Accounting And Reservations

`dsl_dir_dirty()` adds a dsl_dir to the pool dirty list and holds the dbuf until sync. `dsl_dir_sync()` clears current-txg temporary towrite accounting and releases that dirty hold.

The directory-level `parent_delta()` computes how much usage change should propagate to a parent when a reservation may already cover part of the usage.

`dsl_dir_space_available()` recursively combines parent availability, quotas, reservations, pool adjusted size at the root, optional pending writes, and a hypothetical ancestor delta.

Temporary reservation flow:
- `dsl_dir_tempreserve_space()` reserves ARC memory first, then dsl_dir space.
- `dsl_dir_tempreserve_impl()` checks refquota through `dsl_dataset_check_quota()` on the first iteration, checks dsl_dir quota or pool availability, updates `dd_tempreserved`, records reservations in a list, and recurses to parents with adjusted reservation pressure.
- `dsl_dir_tempreserve_clear()` releases both dsl_dir temp reservations and ARC temp reservations.

Actual usage flow:
- `dsl_dir_willuse_space()` records estimated positive space to write and recursively propagates parent deltas.
- `dsl_dir_diduse_space()` updates used/compressed/uncompressed bytes and used-breakdown buckets in syncing context, then propagates accounted deltas and reservation transfers to parents.
- `dsl_dir_transfer_space()` moves used bytes between breakdown categories without changing total usage.

## Quota And Reservation Properties

`dsl_dir_set_quota_check()` predicts the new quota property and rejects values below reservation or used-plus-pending-space when syncing or no pending writes exist. `dsl_dir_set_quota_sync()` writes the property, handles old-pool history logging, and updates cached `dd_quota`.

`dsl_dir_set_reservation_check()` predicts the new reservation, skips precise open-context checks, computes availability at parent/root, and rejects values that cannot fit or exceed quota. `dsl_dir_set_reservation_sync_impl()` updates `dd_reserved` and propagates the reservation delta to ancestors. `dsl_dir_set_reservation_sync()` writes the property and applies the implementation.

## Rename And Transfer Checks

`closest_common_ancestor()` and `would_change()` support movement between branches. `dsl_valid_rename()` validates descendant name lengths and nesting depth after a rename.

`dsl_dir_rename_check()` ensures the source exists, target parent exists, target name is free, pool is unchanged, descendants remain within name/nesting limits, count properties are initialized if filesystem/snapshot limits are active, encryption rules allow the move, the target is not inside the source subtree, and target branch has enough space and limit headroom.

`dsl_dir_rename_sync()` logs before mutation, adjusts filesystem/snapshot counts when moving between parents, transfers used and reserved-child accounting, removes the old parent ZAP entry, changes `dd_myname` and parent object/reference, adds the new parent ZAP entry, notifies property callbacks, and releases holds.

`dsl_dir_transfer_possible()` is the reusable check for moving usage/counts from one branch to another. It computes the common ancestor, adjusts source-side availability impact, checks target space, and checks filesystem/snapshot limits.

## Miscellaneous

`dsl_dir_snap_cmtime()` and `dsl_dir_snap_cmtime_update()` maintain snapshot namespace change time in memory. `dsl_dir_zapify()` converts the dsl_dir object to zapified metadata. `dsl_dir_is_zapified()` detects whether the backing object is zapified.

## Research Notes

This file is the hierarchical accounting authority. Dataset operations depend on it to correctly distinguish head, child, snapshot, refreservation, and child-reservation usage. Rename is especially sensitive because it must move namespace links, space accounting, count-limit state, parent references, and property notifications atomically in syncing context.
