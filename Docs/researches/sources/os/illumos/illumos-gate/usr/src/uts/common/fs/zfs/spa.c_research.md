# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa.c

## Role In The Source Tree

`spa.c` is the central illumos ZFS Storage Pool Allocator implementation for persistent pool-level state transitions. It owns high-level pool lifecycle operations: property get/set, pool open/import/create/export/destroy/reset, root-pool import, auxiliary vdev loading, vdev topology changes, async pool tasks, transaction group syncing, activity waiting, and ZFS sysevent posting.

The file sits above vdev, metaslab, DSL, DMU, ZIO, ZIL, DDT, scrub/scan, MMP, removal, checkpoint, initialize, trim, L2ARC, and feature-flag code. Most of its functions are orchestration points that lock the SPA namespace/config, call lower layers in strict order, and persist derived pool state into MOS objects, vdev labels, and the config cache.

## Major Responsibilities

- Defines ZIO taskq topology per I/O type and priority, including fixed, batch, and multi-taskq modes.
- Provides zpool property retrieval, validation, mutation, and sync-time persistence.
- Activates/deactivates an in-core `spa_t`, including metaslab classes, per-pool taskqs/process, txg root zios, dirty lists, errlists, keystore, and upgrade taskq.
- Loads and unloads pools through staged config parsing, vdev open/validate, uberblock selection, MOS opening, trusted-config replacement, feature checks, aux vdev loading, vdev metadata loading, DDT loading, log verification, pool verification, ZIL claiming, sync-thread startup, and async restart.
- Creates new pools, including vdev labels, MOS directory entries, config object, deferred-free bpobj, DDTs, history, checksum salt, initial properties, txg sync startup, cachefile writes, and create events.
- Imports pools, tries imports for discovery, and imports root pools from boot labels.
- Exports, destroys, or resets pools after quiescing async work, checking references, stopping initialize/TRIM/autotrim work, dirtying final labels, unloading, and updating cachefiles.
- Implements top-level vdev operations: add, attach/replace/spare, detach, split mirror, set path/FRU, initialize, TRIM, scan/scrub entry points, and automatic resilver-completion detach handling.
- Dispatches async pool tasks for config update, remove/probe, autoexpand, resilver, initialize/TRIM/autotrim restart, and L2ARC rebuild.
- Implements the main `spa_sync()` txg pipeline, including config object sync, aux device object sync, error log sync, DSL pool sync, frees/deferred frees, DDT sync, scan sync, removal sync, upgrade sync, metaslab flushing, vdev sync, uberblock/config label rewrite, post-sync cleanup, space accounting, spare polling, and async dispatch.
- Provides activity wait APIs used by `zpool wait`-style operations.
- Posts kernel sysevents for pool and vdev changes.

## Important Data And State

- `zio_taskqs`: static policy table mapping each `ZIO_TYPE_*` and `ZIO_TASKQ_*` lane to taskq creation rules.
- Pool tunables include cachefile retry interval, taskq sizing/binding/system-duty-cycle controls, load verification toggles, missing top-level vdev limits, spare polling interval, and sync pause debug knob.
- `spa->spa_config`, `spa->spa_config_object`, `spa->spa_config_syncing`, and `spa->spa_config_txg` represent the in-core, MOS-backed, currently syncing, and committed pool configuration.
- `spa->spa_root_vdev` is rebuilt from untrusted config and then replaced by MOS-trusted config during normal load.
- `spa->spa_trust_config` gates writeability and strict blkptr/vdev assumptions after the MOS config is loaded.
- `spa->spa_load_info` accumulates import diagnostics such as missing devices, unsupported features, MMP status, rewind data, load time, and data-error counts.
- `spa->spa_spares` and `spa->spa_l2cache` hold auxiliary vdev objects, packed-nvlist MOS object IDs, pending lists, and sync flags.
- `spa->spa_deferred_bpobj`, `spa_free_bplist[]`, log spacemap metadata, and DDT state participate in txg convergence.
- `spa->spa_all_vdev_zaps` and `spa->spa_avz_action` track per-vdev ZAP map initialization, rebuild, or destruction.
- `spa->spa_async_tasks`, `spa->spa_async_thread`, and `spa->spa_async_suspended` coordinate deferred pool maintenance.
- `spa->spa_activities_lock` and related counters/cvars guard race-free waiting for checkpoint discard, frees, initialize, replace, remove, resilver, and scrub activity.

## Lifecycle And Load Path

The load path is deliberately split into small helpers. `spa_load()` records load state and calls `spa_load_impl()`, while `spa_load_best()` wraps it with rewind retry behavior. `spa_load_impl()` first calls `spa_ld_mos_with_trusted_config()`, which parses the supplied config, opens and validates vdevs, selects an uberblock, opens the MOS root block, loads the trusted MOS config, rebuilds/reopens the vdev tree, and can force a reload if the original config omitted too many top-level vdevs.

After a trusted config is established, `spa_load_impl()` optionally rewinds to a checkpoint, reads checkpoint txg metadata, loads indirect vdev/removal metadata, verifies feature support, opens DSL special directories, loads pool properties, opens spares and L2ARC devices, loads vdev metadata and DTLs, loads DDTs, verifies ZIL logs, verifies pool block reachability according to rewind policy, updates deflated-space accounting, claims log blocks, starts sync/MMP threads, writes needed config updates, schedules resilver and restart work, logs history, starts auxiliary zthreads, cleans stale/inconsistent datasets, and restarts initialize/TRIM/autotrim state.

The code distinguishes normal open/import, tryimport, recover/rewind import, checkpoint import, split assembly, verbatim import, and root-pool import. It also distinguishes untrusted cachefile/scan/tryimport configs from MOS-trusted config because missing devices and writeability have different risk profiles in those phases.

## Pool Properties

`spa_prop_get_config()` reports derived state such as size, allocated/free bytes, checkpoint bytes, fragmentation, expandable space, read-only state, capacity, dedup ratio, health, version, GUID, altroot, comment, max block size, max dnode size, and cachefile source. `spa_prop_get()` merges these derived values with persistent MOS pool properties.

`spa_prop_validate()` enforces property-specific rules: feature enable syntax, version upgrade bounds, boolean-like property ranges, multihost hostid requirement, bootfs version/bootability/ZPL/compression validation, failure-mode behavior for suspended pools, cachefile path validation, printable and length-bounded comments, and dedup ditto minimums.

`spa_prop_set()` separates version/feature changes from general property syncing and runs `spa_sync_version()` or `spa_sync_props()` via DSL sync tasks. `spa_sync_props()` writes persistent props into the MOS pool properties ZAP, mutates in-core cached fields, handles feature enables, updates comments in vdev labels, and schedules autoexpand/autotrim async work where needed. `spa_configfile_set()` handles the non-persistent cachefile list.

## Vdev And Auxiliary Device Operations

`spa_config_parse()` recursively builds vdev trees from nvlists by delegating validation/allocation to `vdev_alloc()`. `spa_load_spares()` and `spa_load_l2cache()` reload auxiliary device lists from packed MOS nvlists, open/validate devices, reconcile active spares and L2ARC presence, and regenerate status-rich configs. `spa_validate_aux_devs()` validates proposed spares/L2ARC entries and labels them as auxiliary devices.

Main topology mutation APIs include:

- `spa_vdev_add()` for adding top-level children, spares, and L2ARC devices while avoiding allocation before config labels/cache are safely updated.
- `spa_vdev_attach()` for mirror attach, replace, and spare-in operations, including DTL initialization and resilver restart/defer.
- `spa_vdev_detach()` for mirror/replacing/spare detach, label removal, parent compaction/removal, unspare propagation, DTL cleanup, autoexpand, and history/events.
- `spa_vdev_split_mirror()` for splitting mirror children into a new pool, including log reset, split metadata, temporary offlining, new SPA assembly, property set, original-pool detach, and rollback on failure.
- `spa_vdev_initialize()` and `spa_vdev_trim()` for start/cancel/suspend over selected leaf vdev GUIDs with per-vdev error lists and stop waits.
- `spa_vdev_setpath()` / `spa_vdev_setfru()` for persistent leaf path or FRU updates.

Checkpoint presence or checkpoint discard blocks unsafe topology operations such as attach, detach, and split. Active device removal further constrains add/attach cases.

## Sync Pipeline

`spa_sync()` is the core txg commit routine. It waits for open-context txg zios, acquires config locks, converts pending vdev state dirties into config dirties, creates an assigned DMU tx, programs the deadman cyclic, handles version upgrade edge cases, adjusts allocation queue depths, starts indirect mapping condensation if appropriate, then calls `spa_sync_iterate_to_convergence()`.

`spa_sync_iterate_to_convergence()` repeatedly syncs config and aux objects, error logs, DSL pool state, frees or deferred frees, DDTs, scans, removal state, upgrades, log spacemap/metaslab data, and dirty vdevs until the MOS is clean. `spa_sync_rewrite_vdev_config()` then writes uberblocks/config labels either to selected healthy top-level vdevs or all dirty vdevs, retrying after I/O suspension/resume if necessary.

After committing the DMU tx, `spa_sync()` clears dirty config state, publishes the newly synced config, calls DSL/vdev sync-done paths, evicts old metaslabs, closes syncing log spacemap data, updates deflated space, verifies no late dirties remain, updates `spa_ubsync`, handles ignored writes, polls spare health, and dispatches pending async tasks.

## Import, Export, And Recovery Details

`spa_open_common()` opens pools from the namespace/cachefile, activates unloaded SPAs, applies load policy, handles recover mode, returns load diagnostics on failure, and removes stale exported/destroyed entries. `spa_import()` imports non-root pools from user config and properties, with special verbatim import handling, read-only mode, rewind policy, aux-device replacement from user paths, cachefile updates, autoexpand scheduling, history, and events. `spa_tryimport()` uses a temporary `$import` SPA for discovery, returns generated config and load info, and preserves bootfs/spares/L2ARC visibility.

`spa_export_common()` implements export, destroy, and reset. It suspends async tasks, checks active references, rejects export with active shared spares unless forced, stops initialize/TRIM/autotrim work, marks final pool state for labels, unloads/deactivates, optionally returns old config, writes/removes cachefile state, and removes the SPA from the namespace for real export/destroy.

Recovery support includes safe and extreme rewind in `spa_load_best()`, load verification via pool traversal in `spa_load_verify()`, MMP activity detection in `spa_activity_check_*()`, missing-log handling, checkpoint rewind in `spa_ld_checkpoint_rewind()`, and missing top-level vdev tolerances restricted to read-only trusted-config loads.

## Concurrency And Locking

This file relies on `spa_namespace_lock` for namespace and global lifecycle serialization, `spa_config_enter/exit()` over SCL classes for vdev/config/state synchronization, per-subsystem locks for props, async, proc, scrub, initialize, trim, and activities, and DSL sync tasks for MOS mutations. It is careful to drop namespace/config locks around waits or recursive opens where necessary.

The activity wait subsystem documents and implements a race-free pattern: waiters hold `spa_activities_lock` while checking activity state, temporarily acquire subsystem locks in the same order as completing threads when needed, then wait on a shared cvar. Completers call `spa_notify_waiters()` after state transitions, preventing missed wakeups. `spa_wake_waiters()` cancels and drains waiters during unload/export.

Async tasks are serialized through `spa_async_thread`; `spa_async_suspend()` waits for the thread and suspends removal/condense/checkpoint-discard zthreads, while `spa_async_resume()` restarts them. Config-cache write failures are rate-limited by `zfs_ccw_retry_interval` before redispatch.

## External Interfaces And Dependencies

The file exports or defines many SPA entry points used by ioctl, pool namespace, vdev, scan, and sync code: `spa_prop_get`, `spa_prop_set`, `spa_change_guid`, `spa_open`, `spa_open_rewind`, `spa_import`, `spa_tryimport`, `spa_destroy`, `spa_export`, `spa_reset`, `spa_vdev_add`, `spa_vdev_attach`, `spa_vdev_detach`, `spa_vdev_initialize`, `spa_vdev_trim`, `spa_vdev_split_mirror`, `spa_scan`, `spa_scan_stop`, `spa_scrub_pause_resume`, `spa_sync`, `spa_sync_allpools`, `spa_evict_all`, `spa_lookup_by_guid`, `spa_upgrade`, `spa_wait`, `spa_wait_tag`, and sysevent helpers.

Key dependencies include `vdev_*` for topology/open/label/DTL/config operations, `dsl_pool_*` and `dsl_dataset_*` for MOS/dataset state, `dmu_*` and `zap_*` for object storage, `zio_*` for I/O execution and frees, `zil_*` for log claim/reset/check, `ddt_*` for dedup tables, `metaslab_*` for allocation classes and space accounting, `mmp_*` for multihost protection, `spa_remove`/`spa_condense`/`svr` for device removal, and `l2arc_*` for cache device integration.

## Failure Handling And Diagnostics

Failure paths generally annotate `spa->spa_load_info`, call `spa_load_failed()` or `spa_load_note()`, set vdev aux state through `spa_vdev_err()`, and emit ereports or sysevents. Import failures can return a generated config with vdev states and load diagnostics. MMP failures report remote hostname/hostid when available. Unsupported features are split into read and write support checks so tryimport can report read-only importability.

The file contains deliberate recovery-oriented escape hatches: dry-run load verification for zdb, missing top-level vdev tunables for advanced read-only recovery, missing log import flags, rewind policies, checkpoint preview/rewind distinctions, and verbatim import.

## Notable Invariants And Safety Checks

- Pools with missing top-level vdevs are forced read-only once the trusted config is used.
- Writeability depends on trusted config, avoiding writes based only on cachefile/scan data.
- Normal load rejects unsupported read features; tryimport distinguishes unsupported write features from read-only usability.
- MMP activity checks are skipped only for explicit zdb-like flags, same hostid, clean export, disabled MMP, or unchanged tryimport evidence.
- Topology changes are blocked while checkpoints exist or are being discarded.
- New vdevs are added without metaslab initialization until config labels/cache are safely synced.
- `spa_sync()` must reach MOS convergence before label rewrite and asserts no dirty datasets/dirs/vdev txg entries remain afterward.
- Per-vdev ZAP map operations are transactional and debug-verified when configs are dirty.
- Waiters are cancelled and drained before unload.

## Research Notes

This file is a high-value architecture reference for learning ZFS because it shows how pool-level correctness is assembled from lower layers: nvlist configs, vdev labels, uberblocks, MOS ZAP objects, txg sync, ZIL replay/claim, feature flags, DTLs, MMP, and async repair. Most functions are not local algorithms in isolation; their correctness depends on call ordering, lock ordering, sync-task context, and the distinction between in-core state, MOS state, vdev labels, and user-visible cachefile state.
