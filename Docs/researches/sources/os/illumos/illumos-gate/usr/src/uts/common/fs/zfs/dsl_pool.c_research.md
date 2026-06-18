# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_pool.c

## Role

Implements core ZFS DSL pool lifecycle and synchronization plumbing: opening/creating/closing `dsl_pool_t`, managing MOS/root/special directories, coordinating txg sync work, dirty-space accounting, pool config locking, clone upgrade helpers, and temporary user-hold pool ZAP support.

## Main Responsibilities

- Pool initialization/open/create/close:
  - `dsl_pool_open_impl()` allocates and initializes the in-core pool, txg state, MMP, txg lists, taskqs, mutexes, CVs, and async drain queues.
  - `dsl_pool_init()` opens the MOS from the root block pointer.
  - `dsl_pool_open()` resolves root, `$MOS`, `$ORIGIN`, `$FREE`, `$LEAKED`, free/obsolete bpobjs, scan state, feature objects, and temporary userrefs.
  - `dsl_pool_create()` creates the MOS, pool directory, scan state, root dir, `$MOS`, `$FREE`, free bpobj, origin snapshot, feature ZAPs, encryption feature enablement, root dataset, and root ZPL objset.
  - `dsl_pool_close()` unwinds all held dirs/datasets, bpobjs, objset, txg lists, taskqs, ARC buffers, MMP, scan state, locks, and memory.

## Synchronization Flow

`dsl_pool_sync()` is the central txg sync function. Its ordering is important:

1. Runs early sync tasks before dirty dataset blocks.
2. Writes dirty datasets, waits for their zios, then reconciles dirty-space accounting.
3. Updates user/group/project quota accounting and waits for `dp_sync_taskq`.
4. Re-syncs datasets dirtied by quota updates.
5. Finalizes dataset and dir sync state.
6. Applies accumulated MOS space deltas to `$MOS`.
7. Syncs MOS if dirty.
8. Runs normal sync tasks after data and pre-task MOS sync.
9. Commits the assigned tx.

`dsl_pool_sync_done()` then cleans dirty ZILs and confirms MOS cleanliness for the txg.

## Dirty Space and Throttling

The file defines write throttle tunables such as `zfs_dirty_data_max`, `zfs_dirty_data_sync_pct`, `zfs_delay_min_dirty_percent`, and `zfs_delay_scale`. Dirty bytes are tracked globally and per txg through `dsl_pool_dirty_space()`, `dsl_pool_undirty_space()`, and `dsl_pool_dirty_delta()`. `dsl_pool_need_dirty_delay()` kicks a txg when dirty bytes exceed the sync threshold and reports whether writers should delay.

## Space Availability

`dsl_pool_adjustedsize()` subtracts checkpoint space, deferred frees, and configurable slop reservation from pool allocatable space. `dsl_pool_unreserved_space()` further subtracts deferred metaslab allocation to produce a quota-like availability value used by sync tasks.

## Upgrade and Compatibility Helpers

- `dsl_pool_upgrade_clones()` and `upgrade_clones_cb()` repair old clone/origin metadata and populate next-clone ZAPs.
- `dsl_pool_upgrade_dir_clones()` creates `$FREE` and free bpobj during upgrade and populates `dd_clones`.
- `dsl_pool_create_origin()` creates the hidden `$ORIGIN` dataset/snapshot used by older clone accounting.

## Temporary User Holds

Pool-wide temporary hold state is maintained in `dp_tmp_userrefs_obj`.

- `dsl_pool_clean_tmp_userrefs()` reconstructs hold nvlists from `<dsobj>-<tag>` entries and releases them.
- `dsl_pool_user_hold_create_obj()` creates the pool ZAP lazily.
- `dsl_pool_user_hold()` and `dsl_pool_user_release()` add/remove temporary hold records.

## Locking Model

The long comment near the end documents the `dp_config_rwlock` contract. Holds on datasets/dirs require the config lock. User-visible mutations should generally use sync tasks, while read-only paths manually hold/release the pool and dataset. Long holds may outlive the config lock only when they intentionally prevent destruction.

## Key Dependencies

Works tightly with `dsl_dataset`, `dsl_dir`, `dsl_synctask`, `dsl_scan`, `bpobj`, `bptree`, `spa`, `txg`, `zio`, `zil`, `arc`, feature flags, and ZAP objects.

## Notable Invariants

- Early sync tasks must not dirty metaslabs; `dsl_early_sync_task_verify()` checks relevant free/checkpointing trees.
- Non-MOS datasets must not be synced twice except for the quota-update pass.
- MOS space deltas are accumulated and applied outside MOS syncing.
- Config lock helpers assert against recursive reader entry.
