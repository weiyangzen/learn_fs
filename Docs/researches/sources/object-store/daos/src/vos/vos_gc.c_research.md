# sources/object-store/daos/src/vos/vos_gc.c

## Purpose
`vos_gc.c` implements VOS garbage collection for asynchronously freeing containers, objects, dkeys, akeys, single values, and recx extents after higher-level delete/punch/destroy operations enqueue durable GC items. It supports both traditional pool/container GC bins and bucket-aware GC for evictable metadata pools.

## Important APIs, Types, And Functions
- `struct vos_gc` describes each GC level with name, type, default drain credits, drain callback, and optional free callback.
- `gc_table[]` defines the hierarchy: akey, dkey, object, container.
- `gc_add_item()` appends a durable `vos_gc_item` to the appropriate GC bin and registers the pool/container for later reclaim.
- `gc_drain_btr()`, `gc_drain_evt()`, `gc_drain_key()`, `gc_drain_obj()`, and `gc_drain_cont()` flatten child trees before the parent item is freed.
- `gc_bin_find_bag()`, `gc_bin_add_item()`, `gc_bin_free_bag()`, `bin_get_item()`, and `gc_free_item()` implement persistent ring-style GC bags.
- `gc_reclaim_pool()` is the classic reclaim loop; `gc_reclaim_pool_p2()` is the bucket-aware path for evictable pools.
- `gc_open_pool()`, `gc_open_cont()`, `gc_init_pool()`, `gc_init_cont()`, and close/check helpers initialize and recover GC state.
- `vos_gc_pool()`, `vos_gc_pool_tight()`, `gc_wait()`, `vos_gc_pool_idle()`, `gc_reserve_space()`, `vos_flush_pool()`, and `vos_gc_metrics_init()` are public/runtime integration APIs.

## Control Flow
Deletion paths call `gc_add_item()` inside an existing umem transaction. It chooses the correct bin from pool or container state, optionally using bucket trees for evictable pools, appends the item to a GC bag, registers the pool in TLS GC lists, and links the container on `vp_gc_cont` if needed.

Classic reclaim starts in `gc_reclaim_pool()`: take a container from the fair queue, start one umem transaction, walk from akey upward to container, drain subtrees within credits, free empty items, update stats, and either deregister an empty pool or move it to the tail for later. Container drain destroys DTX tables first, moves leftover container GC bags to pool bins if needed, and drains the object tree.

Evictable-pool reclaim uses `gc_reclaim_pool_p2()`: pin one metadata bucket, start/commit transactions around bucket changes, flatten containers by moving bucket bins to pool bucket trees, pick non-empty bins by bucket, reclaim bins, delete empty bucket-tree records, unpin, update stats, and call `umem_heap_gc()`. This minimizes cache eviction and keeps GC locality aligned with metadata buckets.

## State And Persistence Behavior
GC bins and bags are durable fields in pool/container df structures and extension bucket trees. A bag stores queued `vos_gc_item` records with item offsets and bucket ids. Freeing a GC item is transactional: the bag head is advanced or bag freed/reset, then the real object/key/container/value memory is freed, and stats are updated. Pool registration (`vp_gc_link`, `vp_opened`) and container GC links are volatile but reconstructed on open by checking durable bins and bucket trees.

Pool initialization creates one empty bag for each pool-level GC type. Container initialization starts bins empty because container bins are only needed after object/key deletion. Bucket GC trees are created in pool/container extensions when available. Destroyed containers are not synchronously freed; their `vos_cont_df` is eventually freed by `gc_free_cont()` after DTX tables, object tree, child bags, and extension state are drained.

## Dependencies And Integration Points
GC integrates with dbtree and evtree drain APIs, umem transactions and cache pinning, VEA flushing, VOS DTX table destruction, container/pool reference management, object/key persistent formats, checker validation for GC bucket trees and pool extension padding, telemetry, standalone GC wait, and pool eviction mode.

## Risks And Edge Cases
- GC must not run with an active DTX handle; `vos_gc_yield()` asserts this.
- Container drain destroys DTX tables before yielding, preventing dangling DTX records during subtree drain.
- Persistent bag manipulation uses transactional pointer updates and `UMEM_XADD_NO_SNAPSHOT`; ordering must avoid losing queued items.
- Bucket-aware GC must unpin buckets and close/commit transactions when switching buckets.
- `gc_bags_move()` can transfer container bags to pool bins, and callers must restart at the akey level to avoid missing moved work.
- If GC cannot allocate space, `vp_gc_nospc` forces very small credit slices on later attempts.

## Test Signals
Tests should cover enqueue and drain for every GC type, ring bag wraparound and last-bag reset, container destroy GC including DTX table destruction and extension free, moving container bags to pool bins, classic and evictable-pool reclaim, bucket-tree add/delete and pin switching, pool registration/deregistration reference counts, no-space retry behavior, `vos_gc_pool()` yield modes, metrics counters, checker validation of GC bucket trees, and VEA flush when no GC work remains.
