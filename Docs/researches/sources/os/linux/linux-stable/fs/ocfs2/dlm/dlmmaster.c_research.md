# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmmaster.c

## Purpose

`dlmmaster.c` implements lock-resource ownership for OCFS2 DLM. It manages lock-resource allocation, distributed master election, master-list entries, refmaps, assert-master cleanup, lock-resource dereferencing, lock-resource migration, and cleanup after node death.

The core abstraction is the lock resource owner: exactly one node is master for a lock resource unless the owner is temporarily unknown during mastery, migration, or recovery.

## Master List Entries

Master-list entries, or MLEs, coordinate ownership discovery and migration. The file supports three MLE types:

- `DLM_MLE_MASTER`: local node is trying to master a resource.
- `DLM_MLE_BLOCK`: local node is waiting for another node to master it.
- `DLM_MLE_MIGRATION`: resource ownership is moving from one node to another.

MLEs contain maybe, vote, response, and node maps. They attach to DLM heartbeat events so node up/down changes can restart mastery without allocating in heartbeat callbacks.

Key functions:

- `dlm_init_mle()`
- `dlm_find_mle()`
- `__dlm_insert_mle()`
- `__dlm_unlink_mle()`
- `dlm_put_mle()`
- `dlm_get_mle_inuse()`
- `dlm_put_mle_inuse()`
- `dlm_clean_master_list()`

MLE references are kref-managed and tracked per domain by type counters.

## Lock Resource Allocation

The file owns slab caches for:

- `o2dlm_lockres`
- `o2dlm_lockname`
- `o2dlm_mle`

`dlm_new_lockres()` allocates a lock resource and lock name, initializes queues, wait queues, refcount, owner, state, AST reservation count, migration fields, refmap, LVB, and tracking-list membership.

`dlm_lockres_put()` releases a lock resource once it is unhashed and removed from all queues and lists. Release asserts the resource is no longer on hash, grant, convert, blocked, dirty, recovery, or purge lists.

## Lock Resource Mastery

`dlm_get_lock_resource()` is the main lookup/mastering function. It:

1. Looks for an existing lock resource.
2. Waits if ownership is unknown or dropping-ref is in progress.
3. Pins existing resources with an inflight reference.
4. Allocates a lock resource and MLE if no resource exists.
5. Handles `LKM_LOCAL` by immediately mastering locally.
6. Checks for existing MLEs.
7. Creates a `DLM_MLE_MASTER` if this node should attempt mastery.
8. Sends master requests to peers.
9. Waits until master election completes.
10. Clears `DLM_LOCK_RES_IN_PROGRESS` and wakes waiters.

Master election uses `DLM_MASTER_REQUEST_MSG` and responses:

- `DLM_MASTER_RESP_YES`: peer is master.
- `DLM_MASTER_RESP_NO`: peer is not master.
- `DLM_MASTER_RESP_MAYBE`: peer may also be trying.
- `DLM_MASTER_RESP_ERROR`: retry.

If all votes complete and no peer is known master, the lowest candidate in `maybe_map` wins. The winner asserts mastery to peers.

## Master Request Handler

`dlm_master_request_handler()` answers ownership queries from other nodes. It checks domain state, existing lock resources, resource recovery/migration state, current owner, and local MLEs.

It may:

- Return YES and set the requestor bit in the refmap if this node owns the resource.
- Return NO if another owner is known or this node is blocked.
- Return MAYBE if local mastery is also in progress.
- Create a `DLM_MLE_BLOCK` when the lock resource is not known locally.
- Dispatch assert-master work to clean stale MLEs created on lower-numbered nodes.

## Assert Master

`dlm_do_assert_master()` sends `DLM_ASSERT_MASTER_MSG` to a node map and sets `DLM_LOCK_RES_SETREF_INPROG` while refmap updates are in progress.

`dlm_assert_master_handler()` processes an asserted owner. It validates MLE and lock-resource state, updates MLE master fields, wakes waiters, changes the lock-resource owner, handles migration completion, and returns response flags indicating whether the sender should reassert or set a mastery reference.

`dlm_dispatch_assert_master()` queues asynchronous assert-master work, and `dlm_assert_master_worker()` sends asserts while respecting migration state and AST reservation barriers.

The post handler clears `DLM_LOCK_RES_SETREF_INPROG` and drops the returned lock-resource reference.

## Refmap And Dereference

The refmap tracks which nodes hold a reference to a mastered lock resource.

Key functions:

- `dlm_lockres_set_refmap_bit()`
- `dlm_lockres_clear_refmap_bit()`
- `dlm_drop_lockres_ref()`
- `dlm_deref_lockres_handler()`
- `dlm_deref_lockres_done_handler()`
- `dlm_deref_lockres_worker()`

If a deref arrives while `DLM_LOCK_RES_SETREF_INPROG` is active, work is deferred until assert-master ref setup finishes. Protocol minor 1.3 adds `DLM_DEREF_LOCKRES_DONE` so the non-master can be told when the master has completed the deref and purge-related state can proceed.

## Migration

A lock resource is migratable when:

- It is locally mastered.
- It has no local locks.
- It has non-local locks or refmap references.
- It is not already migrating or recovering.

`dlm_empty_lockres()` is used during domain leave to migrate such resources away.

`dlm_pick_migration_target()` chooses a target from non-local locks first, then refmap references, skipping nodes exiting the domain.

`dlm_migrate_lockres()` performs the original-master side:

1. Allocates a migration buffer and MLE.
2. Adds a migration MLE.
3. Marks the resource migrating after AST/dirty barriers.
4. Flushes assert-master work.
5. Sends the full lock-resource state to the target through `dlm_send_one_lockres()`.
6. Waits for the target to assert mastery.
7. Sets owner to target.
8. Removes nonlocal lock structures and clears remote refmap bits.
9. Recalculates usage and wakes waiters.

`dlm_migrate_request_handler()` runs on third-party nodes when a new master announces migration. It adds a migration MLE and marks any local resource migrating.

`dlm_finish_migration()` runs on the new master after receiving all lock-resource data. It sends migration requests to other nodes, asserts mastery to all nodes except the old master, then asserts back to the old master so the migration completes everywhere.

## AST Reservation And Migration Barrier

Migration depends on AST reservation accounting:

- `__dlm_lockres_reserve_ast()` increments `res->asts_reserved` and refuses to reserve while migrating.
- `dlm_lockres_release_ast()` decrements the count. If migration is pending and this was the last reserved AST, it atomically sets `DLM_LOCK_RES_MIGRATING` and wakes migration waiters.

`dlm_mark_lockres_migrating()` uses this mechanism to block new dirtying, wait for pending AST work to drain, and ensure migration starts only when the lock-resource queues are stable.

## Node Death Cleanup

`dlm_clean_master_list()` handles MLE cleanup after a node dies:

- `DLM_MLE_MASTER` entries are left for their local waiters to notice node-map changes.
- `DLM_MLE_BLOCK` entries are cleaned if the dead node would have been the expected master.
- `DLM_MLE_MIGRATION` entries are cleaned if either old or new master died, unless the target died while the MLE is still actively in use.
- Associated lock resources may have ownership reset to unknown and be moved to recovery.

`dlm_force_free_mles()` is used during domain leave after all peers are gone. It wakes and frees remaining block MLEs.

## Recovery Lock Special Case

`dlm_pre_master_reco_lockres()` handles `$RECOVERY`. It cannot wait for full node recovery before mastering the recovery lock, so it requeries live nodes to ensure none still believe a dead node owns the recovery lock.

## Concurrency And Invariants

This file is highly lock-order sensitive. It follows the domain-level lock order documented in `dlmdomain.c` and uses explicit comments where it must drop and reacquire locks.

Important invariants:

- Only one MLE for a given lock name should be visible in the master hash.
- A lock resource with unknown owner should normally be `DLM_LOCK_RES_IN_PROGRESS`.
- Mastery refmap updates are serialized by `DLM_LOCK_RES_SETREF_INPROG`.
- Migration requires no dirty state and no pending ASTs.
- Lock-resource release requires removal from all hash/list/queue structures.
- Nonlocal locks are removed from the old master after successful migration.

## Dependencies

This file coordinates with:

- `dlmdomain.c` for domain maps, lifecycle, message handler registration, and recovery maps.
- `dlmlock.c` for inflight references and lock-resource acquisition.
- `dlmconvert.c` and unlock/AST paths through shared lock-resource state.
- `dlmrecovery.c` for migration payload send/receive and master requery helpers.
- `dlmthread.c` for dirty-list processing, purge, and usage recalculation.
