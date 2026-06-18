# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_destroy.c

## Role

`dsl_destroy.c` implements destruction of snapshots and head datasets. It handles immediate and deferred snapshot destroy, batched snapshot destroy through ZFS Channel Programs, deadlist collapse, remap deadlist cleanup, old synchronous destroy for pre-async-destroy pools, async destroy via bptree, dsl_dir teardown, and cleanup of inconsistent datasets.

It is tightly coupled to `dsl_dataset.c`, `dsl_deadlist.c`, `dsl_dir.c`, scan state, feature flags, ZAP metadata, and DMU traversal.

## Snapshot Destroy Checks

`dsl_destroy_snapshot_check_impl()` requires the target to be a snapshot, have no long holds, and, for non-deferred destroy, have no userrefs and not be a branch point (`ds_num_children > 1`). Deferred destroy requires pool support for userrefs and is allowed even when userrefs or children prevent immediate deletion.

`dsl_destroy_snapshot_check()` treats missing snapshots as success so destroy operations are idempotent from the caller’s perspective.

## Snapshot Destroy Sync

`dsl_destroy_snapshot_sync_impl()` is the main snapshot deletion engine. It:
- handles deferred destroy by setting `DS_FLAG_DEFER_DESTROY`,
- logs history before namespace removal,
- notifies the scrub/scan subsystem,
- deactivates per-dataset features,
- rewires previous and next snapshot links and next-clones references,
- updates previous snapshot unique bytes when a deadlist range becomes unique,
- subtracts snapshot-used space,
- moves freed blocks from the next snapshot deadlist to the pool free bpobj,
- merges the destroyed snapshot deadlist into the next dataset’s deadlist,
- handles remap deadlist transfer/obsolete movement,
- collapses deadlist key ranges in clone heads and the head dataset,
- recalculates head unique bytes when deleting the most recent snapshot,
- adjusts refreservation accounting,
- evicts objsets before final free,
- removes the snapshot from the head snapnames ZAP,
- clears bootfs if needed,
- frees next-clones, properties, userrefs, and zapified dataset metadata,
- releases the dsl_dir reference.

Old-format deadlists are handled by `process_old_deadlist()`, which iterates the next deadlist’s old `bpobj`, either keeps blocks on the deadlist or frees them, updates previous unique bytes, adjusts snapused, and swaps deadlist objects.

## Remap Deadlist Handling

`dsl_destroy_snapshot_handle_remaps()` handles device-removal remap deadlists. It moves remap entries from the next snapshot to the pool obsolete bpobj for entries that are no longer referenced by surviving snapshots. It also merges the destroyed snapshot’s remap deadlist into the next dataset, creating the next remap deadlist if necessary, then destroys the old remap deadlist and decrements obsolete-counts feature state.

## Batched Snapshot Destroy

`dsl_destroy_snapshots_nvl()` normalizes the caller’s nvlist, wraps arguments for Lua, and evaluates a ZFS Channel Program. The Lua program first checks all snapshots, removes missing ones, accumulates errors, and only if there are no errors runs sync destroy for each. Returned int64 errors are converted to documented int32 errlist values.

`dsl_destroy_snapshot()` is a single-name wrapper around the nvlist path.

## Head Dataset Destroy

`dsl_destroy_head_check_impl()` requires a head dataset, expected long-hold count, no normal snapshots of the head, no child filesystems, and, for special clone cases, no blocking holds on a deferred-destroy origin snapshot that can be removed together.

`dsl_destroy_head()` unmounts clone origins in kernel builds, checks async-destroy support, and for old pools marks the dataset inconsistent before freeing all objects in open context to keep the sync transaction short. It then runs the actual sync destroy.

`dsl_destroy_head_sync_impl()`:
- logs history and scan destruction,
- detects whether a deferred-destroy origin snapshot should also be removed,
- clears dataset refreservation,
- deactivates dataset features,
- updates clone origin metadata and child counts,
- closes/frees normal and remap deadlists,
- destroys the ZIL,
- either traverses/frees blocks synchronously on old pools or adds the root bp to the pool async-destroy bptree,
- transfers used space to the free dir,
- removes clone references,
- evicts objsets,
- clears `dd_head_dataset_obj`,
- destroys snapnames and bookmarks ZAPs,
- clears bootfs,
- frees the dataset object,
- destroys the containing dsl_dir,
- optionally destroys the now-unreferenced deferred origin snapshot.

`dsl_dir_destroy_sync()` tears down the directory object: decrements parent filesystem counts, removes reservations, asserts zero usage, destroys crypto keys, child/properties/clones/delegation ZAPs, removes the child entry from the parent, and frees the dsl_dir object.

## Inconsistent Dataset Cleanup

`dsl_destroy_inconsistent()` is a `dmu_objset_find()` callback that destroys datasets marked inconsistent unless they still contain resumable receive state. It always returns 0 so the scan continues even if one dataset cannot be processed.

## Research Notes

Destroy paths are intentionally conservative and history is logged before namespace changes. The most delicate sections are deadlist key collapse, remap obsolete movement, async destroy feature activation, and clone/deferred-origin cleanup. This file assumes sync context and pool config writer lock for the major on-disk rewrites.
