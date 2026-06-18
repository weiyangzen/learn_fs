# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_dataset.c

## Role

`dsl_dataset.c` is the main ZFS DSL dataset implementation. It owns dataset lifetime, block accounting, dataset holds/ownership, snapshot creation and rename, temporary snapshots, rollback, clone promotion, clone swap, dataset-level quotas/reservations, dataset statistics, resume receive token reporting, per-dataset feature flags, and remap deadlist management.

It is the central bridge between object-set/block activity and higher-level dataset namespace state. It calls into `dsl_dir.c` for hierarchical space/count accounting, `dsl_deadlist.c` for dead block tracking, `dsl_destroy.c` for snapshot/head teardown helpers, `dsl_deleg.c` indirectly through creation permissions, and the DMU/SPA layers for object allocation, ZAP metadata, feature activation, encryption, scan hooks, and sync task orchestration.

## Main State And Invariants

Important persistent state lives in `dsl_dataset_phys_t`, accessed through `dsl_dataset_phys(ds)`: previous/next snapshot links, deadlist object, snapnames ZAP, referenced/compressed/uncompressed/unique bytes, dataset GUIDs, creation txg/time, flags, and root block pointer.

Runtime state in `dsl_dataset_t` includes:
- `ds_dbuf`, `ds_object`, `ds_dir`, `ds_prev`, and `ds_objset`.
- `ds_deadlist`, `ds_pending_deadlist`, and optional `ds_remap_deadlist`.
- `ds_lock`, `ds_bp_rwlock`, `ds_opening_lock`, `ds_sendstream_lock`, `ds_remap_deadlist_lock`.
- `ds_owner` and `ds_longholds` for mounted/owned dataset protection.
- `ds_feature[]` and `ds_feature_activation[]` for per-dataset feature state.

Key invariants:
- Snapshots are recognized by nonzero `ds_num_children`; heads have `ds_next_snap_obj == 0`.
- Dirtying a snapshot panics; dirtying a head must be after its previous snapshot txg.
- Dataset space changes are mirrored into dsl_dir accounting, with `parent_delta()` adjusting for refreservation.
- Snapshot operations are sync-task based and usually require the pool config lock.
- Long holds prevent destruction and constrain rollback/clone-swap handoff.

## Block Accounting

`dsl_dataset_block_born()` accounts newly born non-hole blocks, updates referenced/compressed/uncompressed/unique bytes, activates large block and checksum features when needed, and propagates head space to the containing dsl_dir. MOS blocks are accounted directly to pool MOS usage.

`dsl_dataset_block_kill()` handles removal. Blocks born after the previous snapshot are freed immediately and subtracted from unique/referenced accounting. Older blocks go to the dataset deadlist or pending deadlist when called from async write-done context. It also updates previous snapshot unique bytes when appropriate and transfers space from head to snapshot usage.

`dsl_dataset_block_remapped()` handles indirect-vdev remapping. If the remapped birth is after the previous snapshot, the segment is obsolete in the vdev. Otherwise it synthesizes a block pointer and stores it in the remap deadlist, creating that deadlist on demand.

## Dataset Opening, Holds, Ownership

`dsl_dataset_hold_obj()` is the constructor/open path. It validates object type, allocates and initializes `dsl_dataset_t`, opens the parent `dsl_dir`, initializes locks/refcounts/lists, loads per-dataset features from zapified dataset metadata, opens the previous snapshot for heads, counts userrefs for snapshots, reads refquota/refreservation, handles encryption errata checks, opens the deadlist/remap deadlist, installs the dmu buffer user, and assigns a unique fsid GUID.

Name-based holds go through `dsl_dataset_hold_flags()`, which first holds the dsl_dir and then optionally resolves `@snapshot` names through the head dataset’s snapnames ZAP. Decrypting holds call `dsl_dataset_create_key_mapping()` and releasing them removes the mapping.

Ownership is layered on top of holds through `dsl_dataset_tryown()`, `dsl_dataset_own*()`, `dsl_dataset_disown()`, and long holds. `dsl_dataset_handoff_check()` temporarily drops an owner long hold during syncing checks to verify no other long holds exist.

## Snapshot Creation And Rename

Snapshot validation is split between `dsl_dataset_snapshot_check()` and `dsl_dataset_snapshot_check_impl()`. It checks:
- no duplicate snapshot in the same txg,
- no name conflict,
- not inconsistent unless part of receive,
- filesystem/snapshot limits,
- enough space for refreservation side effects.

For multi/recursive snapshots, it rolls up per-parent snapshot counts in an nvlist before checking limits so sibling and recursive operations are evaluated as a complete batch.

`dsl_dataset_snapshot_sync_impl()` creates the snapshot dataset object, copies root block and accounting from the head, copies per-dataset features, rewires previous/next snapshot links and next-clones metadata, handles refreservation transfer, clones/rekeys the head deadlist, moves any remap deadlist to the snapshot, writes encryption ivset metadata when appropriate, inserts the snapshot into the snapnames ZAP, updates `ds_prev`, calls scan hooks, updates snapshot cmtime, and logs history.

`dsl_dataset_snapshot()` handles old-pool ZIL suspension for pools before fast snapshots and runs the sync task. `dsl_dataset_snapshot_tmp()` creates a temporary snapshot with a user hold and immediately defers its destroy.

Snapshot rename uses `dsl_dataset_rename_snapshot_check*()` and `dsl_dataset_rename_snapshot_sync*()`, optionally recursively. It checks old-name existence, new-name absence, full name length, logs before mutation, removes the old snapname entry, updates `ds_snapname`, and adds the new ZAP entry.

## Sync, Stats, And Resume Tokens

`dsl_dataset_sync()` writes fsid GUID changes, stores resumable receive progress fields when present, syncs the object set, and activates delayed per-dataset features. `dsl_dataset_sync_done()` drains the pending deadlist into the real deadlist, destroys synced dnode lists, clears raw-write flags, asserts clean objset state, and releases the dirty hold.

Statistics are provided through many `dsl_get_*()` helpers and `dsl_dataset_stats()`. It reports referenced, available, used, ratios, creation txg/time, GUID, objset ID, userrefs, defer-destroy, written space since previous snapshot, clone lists for snapshots, dsl_dir stats for heads, encryption stats, and receive resume token state.

Resume token generation packs selected ZAP resume fields into an nvlist, compresses it with gzip, checksums it with Fletcher4, and hex-encodes it in the send token format. For failed incremental receives, the code also checks the child `%recv` dataset.

## Rollback, Promotion, Clone Swap

Rollback requires a head dataset with a latest snapshot, optional target snapshot matching the latest snapshot, no later bookmarks, no conflicting holds, and quota/refreservation feasibility. Sync creates a `%rollback` clone of the previous snapshot, swaps it with the head through clone-swap logic, zeros the ZIL, then destroys the temporary clone.

Promotion builds snapshot lists for shared, clone, and origin snapshots. `dsl_dataset_promote_check()` validates promotability, encryption roots, long holds, snapshot name conflicts, namespace length, space transfer, filesystem/snapshot limit transfer, and used-snapshot accounting. `dsl_dataset_promote_sync()` rewires origin and clone ancestry, moves snapshot ZAP entries and dsl_dir ownership, updates clone references, transfers space/count accounting, updates origin unique bytes, runs crypto sync hooks, and logs history.

`dsl_dataset_clone_swap_check_impl()` validates that two heads can swap, including branch relationships, modification state, long holds, refreservation availability, and refquota slack. `dsl_dataset_clone_swap_sync_impl()` swaps per-dataset features, evicts objsets, recomputes origin unique bytes, swaps root block pointers, adjusts directory accounting, swaps dataset accounting, swaps deadlists/remap deadlists, calls scan hooks, and logs.

## Quotas, Reservations, Written Space, Remap Deadlists

`dsl_dataset_check_quota()` works with `dsl_dir_tempreserve_impl()` to enforce refquota while discounting unconsumed refreservation. Refquota/refreservation setters are sync tasks that validate feature support, dataset type, predicted property values, current referenced/unique space, dsl_dir availability, and quota interactions before storing properties and updating cached runtime values/accounting.

`dsl_dataset_space_written()` computes space written between an older snapshot and a later snapshot/head by subtracting referenced space and adding relevant deadlist ranges. `dsl_dataset_space_wouldfree()` computes reclaimable space if a contiguous snapshot range is destroyed.

Remap deadlist helpers zapify the dataset as needed, store/remove `DS_FIELD_REMAP_DEADLIST`, open/close/free the remap deadlist, and increment/decrement `SPA_FEATURE_OBSOLETE_COUNTS`. `dsl_dataset_create_remap_deadlist()` clones the normal deadlist and requires the device-removal feature to be active.

## Research Notes

This file is the highest-risk coordination point in the group. Changes here must preserve sync-task atomicity, dsl_dir accounting symmetry, snapshot-chain invariants, deadlist key ranges, encryption errata behavior, and hold/owner semantics. Many helpers assume pool config locks and syncing context rather than performing defensive locking locally.
