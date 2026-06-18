# sources/object-store/daos/src/vos/vos_obj_index.c

## Purpose
`vos_obj_index.c` implements the persistent object index table: a btree keyed by `daos_unit_oid_t` whose records are durable object records (`vos_obj_df` or phase-2 `vos_obj_p2_df`). It also provides object-level iteration, aggregation, punch cleanup, layout-version upgrade support, and bucket-iteration skipping.

## Important APIs, Types, And Functions
Important functions include object-index btree callbacks `oi_rec_alloc`, `oi_rec_free`, `oi_rec_fetch`, `oi_node_alloc`, lookup/update APIs `vos_oi_exist`, `vos_oi_find`, `vos_oi_alloc`, `vos_oi_find_alloc`, `vos_oi_punch`, `vos_oi_delete`, `vos_oi_upgrade_layout_ver`, object iterator operations, `oi_iter_check_punch`, `oi_iter_aggregate`, `vos_bkt_iter_skip`, and `vos_obj_tab_register`. `struct vos_oi_iter` wraps generic iterator state with a dbtree handle, epoch range, container ref, ilog fetch state, punch epoch, bucket iterator, and flags.

## Control Flow
Allocation creates a durable object record, initializes its ilog, sets the object ID, and may force DTX sync for newly created objects. Lookup fetches the btree record and adds ilog timestamp dependencies. Punch updates the object ilog through `vos_ilog_punch`. Iteration prepares a dbtree iterator on the container object table, probes by anchor, filters entries through callback and ilog visibility checks, and fills `vos_iter_entry_t` with object metadata and child type. Aggregation checks discard/aggregation conflicts, aggregates the object ilog, and deletes empty object records from the btree.

## State And Persistence
Persistent state includes object IDs, object ilogs, dkey tree roots, sync/max-write metadata, and optional evictable bucket IDs. Record free destroys ilogs, evicts timestamp cache state, and places objects on the GC heap; during layout upgrade it can delete only the old index entry while preserving shared ilog/tree state. Deletions and aggregation run inside umem transactions.

## Dependencies And Integration Points
The module depends on dbtree class registration, VOS ilog and timestamp APIs, GC, object cache eviction, aggregation/discard conflict checks, container handles, VEA/bucket iteration for md-on-ssd, and generic iterator dispatch. Pool layout versioning and upgrade code relies on the ability to duplicate an object record under a new OID layout version without reallocating trees.

## Risks
Risks include corrupting shared ilog/tree state during layout upgrades, failing to evict cached objects before deleting durable records, mishandling uncertain creates during iteration, and incorrectly skipping bucket ranges in evictable pools. `oi_rec_free` must keep GC and ilog destruction semantics aligned with whether only the index entry is being removed.

## Test Signals
Tests should verify object find/alloc/delete idempotence, object ilog punch and aggregate cleanup, iterator filtering and anchor progress, layout-version upgrade sharing, timestamp conflict behavior, bucket skip bitmaps, and class registration/overhead consistency.
