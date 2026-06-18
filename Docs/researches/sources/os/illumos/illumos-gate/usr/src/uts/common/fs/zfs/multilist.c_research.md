# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/multilist.c

## Scope

This file implements `multilist_t`, a sharded list abstraction used by ZFS to reduce lock contention while preserving normal list operations within independently locked sublists. The file was read completely.

## APIs And Entry Points

- Creation/destruction: `multilist_create()`, internal `multilist_create_impl()`, `multilist_destroy()`.
- Whole-list operations: `multilist_insert()`, `multilist_remove()`, `multilist_is_empty()`, `multilist_get_num_sublists()`, `multilist_get_random_index()`.
- Sublist operations: `multilist_sublist_lock()`, `multilist_sublist_lock_obj()`, `multilist_sublist_unlock()`, insert head/tail, remove, move forward, head/tail/next/prev.
- Link helpers: `multilist_link_init()`, `multilist_link_active()`.

## Control Flow

A multilist owns an array of `multilist_sublist_t`, each with its own mutex and illumos `list_t`. The creator supplies the object size, offset of the embedded `multilist_node_t`, and an index function that maps objects to sublists. `multilist_create()` chooses the sublist count from `zfs_multilist_num_sublists` or defaults to at least four and typically CPU count.

Insert and remove compute the target sublist from the index function, acquire the sublist lock if the caller does not already hold it, and operate on the embedded list node. Sublist APIs expose explicit locking so callers can traverse or batch operations on a shard without locking the whole multilist. `multilist_is_empty()` checks each sublist independently, so concurrent mutation means its result is a moment-in-time approximation rather than a globally locked snapshot.

## State And Dependencies

State is limited to `ml_offset`, `ml_num_sublists`, `ml_index_func`, and the sublist array. It depends on `list_t`, kernel mutexes, ZFS allocation helpers, DTrace probes, CPU count, and `spa_get_random()` for random sublist selection.

In this group, `metaslab.c` uses multilists for the metaslab class TXG list, allowing eviction and selected-TXG ordering to scale across sublists.

## Risks And Invariants

- The index function must be stable for an object while inserted. Removing with a different computed sublist is undefined.
- Direct sublist insertion can place an object in a sublist that differs from its index function; callers must then avoid whole-list remove semantics unless the index matches.
- The lock recursion pattern depends on `MUTEX_HELD()` accurately reporting ownership by the current thread.
- `multilist_sublist_move_forward()` must only remove/reinsert the requested object; ARC eviction relies on that behavior.

## Summary

`multilist.c` is a small concurrency utility: it trades global list ordering for sharded locking and lower contention. Its correctness rests on stable object-to-sublist mapping and disciplined use of explicit sublist locks during traversal.
