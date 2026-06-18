# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmmaster.c

## Purpose
Implements OCFS2 DLM mastership: lock-resource allocation, master-list entries, master discovery, assert-master cleanup, refmap dereference, lock-resource migration, and recovery cleanup for mastership state.

## Main Entry Points
- `dlm_get_lock_resource()` finds, allocates, hashes, masters, or waits for a lock resource.
- `dlm_master_request_handler()` handles remote mastership probes.
- `dlm_assert_master_handler()` handles mastership assertions and MLE cleanup.
- `dlm_dispatch_assert_master()` queues asynchronous assert-master work.
- `dlm_drop_lockres_ref()` and deref handlers maintain remote reference maps.
- `dlm_empty_lockres()` migrates lock resources during domain leave.
- `dlm_finish_migration()` completes migration on the new master.
- `dlm_clean_master_list()` cleans MLEs after node death.
- Cache lifecycle functions initialize/destroy lockres, lockname, and MLE slab caches.

## MLE Model
Master List Entries represent in-progress mastership decisions:
- `DLM_MLE_MASTER`: local node is trying to master a resource.
- `DLM_MLE_BLOCK`: local node is blocking because another node may master it.
- `DLM_MLE_MIGRATION`: mastership is moving from one node to another.

MLEs carry `node_map`, `vote_map`, `response_map`, `maybe_map`, `master`, `new_master`, waitqueue state, refcount, and heartbeat event linkage. Heartbeat callbacks update MLE node maps so mastership waits can restart when nodes join or die.

## Master Discovery
`dlm_get_lock_resource()` first checks the lockres hash. Existing resources are pinned with an inflight reference after waiting for unknown owner or dropping-ref state. New resources are inserted while marked `DLM_LOCK_RES_IN_PROGRESS`, then mastership is resolved through MLEs and `DLM_MASTER_REQUEST_MSG`.

`dlm_wait_for_lock_mastery()` waits until votes complete, another master is asserted, or the local node is the lowest possible master. If local wins, it calls `dlm_do_assert_master()` and sets lockres owner. Node-map changes call `dlm_restart_lock_mastery()`.

## Master Request and Assert
`dlm_master_request_handler()` answers `YES`, `NO`, `MAYBE`, or `ERROR` based on local lockres ownership, in-progress state, MLE type, and migration/recovery state. If this node owns the resource, it sets the requester’s refmap bit and may dispatch assert-master cleanup to lower nodes.

`dlm_assert_master_handler()` validates any local MLE and lockres state, records the asserting node as master, wakes waiters, updates lockres owner, handles migration completion assertions, returns whether this node needs a mastery ref, and requests reassertion if prior master requests reached other nodes.

## Refmap Dereference
`dlm_drop_lockres_ref()` tells the master to clear this node from a lockres refmap. If `DLM_LOCK_RES_SETREF_INPROG` is active, `dlm_deref_lockres_handler()` defers cleanup to `dlm_deref_lockres_worker()` and later sends `DLM_DEREF_LOCKRES_DONE`. This prevents races between assert-master ref propagation and dereference.

## Migration
A migratable lock resource is locally mastered, has no local locks, is not already migrating/recovering, and has nonlocal locks or remote refmap bits. `dlm_migrate_lockres()` installs a migration MLE, marks the lockres migrating after AST/dirty activity drains, sends full lockres state to the target, waits for the target assert, switches owner, removes nonlocal locks, and recalculates usage.

`dlm_finish_migration()` runs on the new master. It notifies other nodes with `DLM_MIGRATE_REQUEST_MSG`, asserts mastership to all except the old master, then asserts back to the old master last, sets itself as owner, clears migration state, and dirties/kicks the resource for normal processing.

## Recovery Cleanup
`dlm_clean_master_list()` removes or wakes MLEs affected by a dead node. Migration MLEs reset associated lockres ownership to unknown if either old or new master died, moving the resource to recovery. `dlm_force_free_mles()` wakes and frees remaining block MLEs during final domain leave.

## Locking and Invariants
The file heavily relies on the domain lock order documented in `dlmdomain.c`. Lock-resource release asserts the resource is unhashed and absent from all queues/lists. AST reservation and release are integral to migration: the final AST release can atomically set `DLM_LOCK_RES_MIGRATING` and wake migration waiters.
