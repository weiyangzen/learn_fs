# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_deadlist.c

## Role

`dsl_deadlist.c` implements ZFS DSL deadlists: per-dataset structures that track blocks killed after particular snapshot boundaries. Deadlists are central to snapshot space accounting, clone promotion, snapshot destroy, rollback, and device-removal remap accounting.

A modern deadlist is a ZAP object whose keys are minimum txg boundaries and whose values are `bpobj` object IDs. Each `bpobj` stores block pointers for blocks born in a txg range. Older pools can store a deadlist directly as a single old-format `bpobj`; most functions preserve compatibility with this format.

## Concurrency Model

The file starts with the concurrency contract:
- Deadlists are modified only from the syncing thread.
- Except for `dsl_deadlist_insert()`, modifications require `dp_config_rwlock` held as writer.
- Accessors such as `dsl_deadlist_space()` and `dsl_deadlist_space_range()` can run concurrently from open context while the config lock is reader-held.
- `dl_lock` protects cached aggregate counters and lazy AVL loading.
- `bpobj_t` provides its own locking; `dl_oldfmt` is immutable while open.

## Data Structures

The in-memory modern deadlist lazily loads a `dl_tree` AVL of `dsl_deadlist_entry_t`, sorted by `dle_mintxg`. Each entry opens a `bpobj` for that boundary. `dsl_deadlist_load_tree()` populates this tree from the ZAP and marks `dl_havetree`.

Persistent aggregate totals live in `dsl_deadlist_phys_t`: used, compressed, and uncompressed bytes. Old-format deadlists do not have this header and delegate directly to `bpobj`.

## Open, Close, Allocate, Free

`dsl_deadlist_open()` initializes the mutex, bonus-holds the object, detects old-format `DMU_OT_BPOBJ`, and either opens the old `bpobj` or points `dl_phys` at the deadlist header. `dsl_deadlist_close()` closes all opened `bpobj`s, destroys the AVL if loaded, releases the dbuf, destroys the mutex, and clears state.

`dsl_deadlist_alloc()` creates either a legacy `bpobj` or a modern ZAP with deadlist header based on pool version. `dsl_deadlist_free()` frees either a single `bpobj` or every child `bpobj` referenced by the ZAP, accounting for the pool empty bpobj special case, then frees the deadlist object.

## Insertion And Key Management

`dsl_deadlist_insert()` inserts a block pointer into the correct `bpobj` bucket. It updates aggregate `dl_used`, `dl_comp`, and `dl_uncomp`, finds the entry whose `mintxg` is immediately before the block birth, and enqueues the block. If that entry currently points to the shared empty bpobj, `dle_enqueue()` allocates a real `bpobj`, decrements the empty bpobj reference, updates the ZAP key, and enqueues there.

`dsl_deadlist_add_key()` adds a new empty boundary greater than existing keys. `dsl_deadlist_remove_key()` removes a boundary and merges its `bpobj` into the previous boundary via `dle_enqueue_subobj()`. These operations are how snapshot creation/destruction collapses or extends deadlist txg ranges.

`dsl_deadlist_regenerate()` rebuilds a modern deadlist key structure by walking dataset previous-snapshot links. It is used when cloning an old-format deadlist into a modern deadlist.

## Clone, Space Queries, Merge, Move

`dsl_deadlist_clone()` creates a new deadlist and copies only key boundaries below `maxtxg`, using empty `bpobj`s. It does not copy actual block pointers; the new deadlist starts as a structural clone used by new snapshots/heads.

`dsl_deadlist_space()` reports aggregate totals. For old format it calls `bpobj_space()`, and for modern format it reads cached header totals under `dl_lock`.

`dsl_deadlist_space_range()` sums `bpobj_space()` across entries in `(mintxg, maxtxg]`. It asserts that missing `mintxg` means no later entries exist, reflecting the invariant that callers supply actual deadlist keys unless querying through `UINT64_MAX`.

`dsl_deadlist_merge()` merges another deadlist object into an open deadlist. Old-format sources are iterated block-by-block. Modern sources move each child `bpobj` into the destination by birth key, remove the source ZAP key, then zero the source deadlist header.

`dsl_deadlist_move_bpobj()` removes all entries at or after `mintxg`, enqueues their child `bpobj`s into a destination `bpobj`, subtracts their aggregate space from the deadlist header, removes ZAP keys, and frees in-memory entries. Snapshot destroy uses this to move now-free blocks to pool free/obsolete lists.

## Research Notes

This file’s important subtlety is that modern deadlists separate key structure from block storage. Cloning generally copies key buckets, not contents. Destroy/merge paths move sub-objects rather than copying individual blocks when possible. Any change here must preserve the exact `(mintxg, maxtxg]` semantics because dataset written-space, would-free, promotion, rollback, and remap accounting all depend on those boundaries.
