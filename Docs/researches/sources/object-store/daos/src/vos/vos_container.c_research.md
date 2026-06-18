# sources/object-store/daos/src/vos/vos_container.c

## Purpose
`vos_container.c` implements the VOS container API and container UUID iteration. It owns creation, open/close, destruction, query, stable-epoch tracking, persisted container properties, and the volatile open-handle cache for `struct vos_container`.

## Important APIs, Types, And Functions
- `struct cont_df_args` passes a persistent `vos_cont_df` pointer and pool into container btree callbacks.
- `vct_ops` defines the persistent container-table btree class: hash key generation, record allocation/free/fetch/update.
- `vos_cont_create()` inserts a new `vos_cont_df` record in the pool container tree.
- `vos_cont_open()` builds the in-memory container handle, opens the object btree, initializes GC, volatile DTX active/committed btrees, DTX LRU array, VEA hints, and reindexes active DTX state.
- `vos_cont_close()` decrements the open count, evicts object-cache entries at last close, and drops the uhash reference.
- `vos_cont_destroy()` removes the persistent container record after ensuring no open handle exists, flushing WAL metadata, and deleting from the pool container btree inside an umem transaction.
- `vos_cont_iter_ops` exposes `VOS_ITER_COUUID` iteration over container UUIDs.
- `vos_cont_get_local_stable_epoch()`, `vos_cont_get_global_stable_epoch()`, `vos_cont_set_global_stable_epoch()`, `vos_cont_set_mod_bound()`, and `vos_cont_save_props()` manage stable epoch and container-extension metadata.

## Control Flow
Creation looks up the UUID, begins an umem transaction, and `dbtree_update()` invokes `cont_df_rec_alloc()`. Allocation persists `vos_cont_df`, its extension, GC bins, and the object table root. Open first checks the in-memory handle hash by container UUID plus pool UUID; an existing handle only increments `vc_open_count`. A cold open fetches the durable `vos_cont_df`, allocates `struct vos_container`, opens GC and object btree state, allocates DTX volatile structures, loads VEA hints, sets `vc_mod_epoch_bound`, reindexes active DTX blobs, then inserts the handle into the uhash and pool container list.

Destroy first invalidates dedup state, rejects open containers, flushes the WAL header, starts a transaction, rechecks for a concurrent reopen, and deletes the container-tree record. The btree free callback does not directly free the full subtree; it evicts timestamp state and enqueues the container for GC with `GC_CONT`. `vos_cont_destroy()` then waits for GC.

## State And Persistence Behavior
Persistent state lives in `vos_cont_df`, `vos_cont_ext_df`, the object tree root, container GC bins, DTX active/committed blob heads and tails, and stable/container property fields in the extension. In-memory state includes open count, uhash link, object btree handle, DTX LRU array and volatile btrees, DTX ordering lists, VEA hint contexts, GC link, DTX counters, local stable epoch, and mod-epoch boundary.

Local stable epoch is calculated from active DTX ordering lists and `vos_agg_gap`, never moving backwards. It also advances `vc_mod_epoch_bound`, which rejects old modifications after a stable epoch has been reported. Global stable epoch is persisted in the container extension, can only move forward, and cannot exceed the local stable epoch.

## Dependencies And Integration Points
The file depends on DAOS dbtree, uhash, umem, VEA hints, GC, DTX, object cache, WAL flush, dedup invalidation, timestamp eviction, checksum/container property structures, and iterator framework. It is the integration point between pool handles and object/DTX/GC subsystems.

## Risks And Edge Cases
- Open error handling calls `cont_free_internal()` for partially initialized handles; the function must tolerate invalid DTX handles and unloaded hints.
- Destroy has a race window around WAL flush and transaction begin, so it explicitly rechecks for container reopen before deleting persistent state.
- Stable-epoch calculations trade precision for O(1)/O(N) DTX list handling, especially for unsorted or reindexed DTX entries.
- Older pool versions or containers without extensions cannot support global stable epoch or saved properties.
- `cont_df_rec_free()` enqueues GC rather than synchronously freeing container contents, so GC correctness is required for durable deletion.

## Test Signals
Tests should cover create duplicate, open cached and cold paths, partial open failure cleanup, close last handle object-cache eviction, destroy busy and race-reopen paths, container UUID iteration anchors, local stable epoch with sorted/unsorted/reindex DTX entries, monotonic global stable epoch enforcement, and property save idempotence for checksum/chunksize fields.
