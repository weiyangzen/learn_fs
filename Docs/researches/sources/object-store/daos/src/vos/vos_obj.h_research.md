# sources/object-store/daos/src/vos/vos_obj.h

## Purpose
`vos_obj.h` declares the internal object cache and object-index API used by VOS object I/O, iteration, aggregation, discard, and metadata management. It defines the central DRAM `struct vos_object` wrapper around a durable object record.

## Important APIs, Types, And Functions
`struct vos_object` contains the LRU link, cached ilog fetch state, object ID, open dkey tree/iterator handles, sync epoch, durable `vos_obj_df` pointer, container back-reference, md-on-ssd pin handle, evictable bucket IDs, mutex/condition variables, zombie/discard/aggregate flags, and bucket loading/allocation state. Flag bits include `VOS_OBJ_VISIBLE`, `VOS_OBJ_CREATE`, `VOS_OBJ_DISCARD`, and `VOS_OBJ_AGGREGATE`. Declared APIs include `vos_obj_hold`, `vos_obj_release`, cache creation/destruction/eviction, `vos_oi_find`, `vos_oi_alloc`, `vos_oi_find_alloc`, `vos_oi_punch`, `vos_oi_delete`, `vos_obj_incarnate`, and `vos_obj_check_discard`.

## Control Flow
Callers usually hold or acquire an object from the LRU cache, optionally incarnate it in a transaction, perform tree/ilog work, and release it with flags that clear discard or aggregation ownership. The header documents that `vos_obj_hold` runs outside local transactions while `vos_obj_incarnate` is used inside a transaction to create negative cache entries or validate updates.

## State And Persistence
The header separates transient cache state from persistent object state. `obj_df` points into PMEM/BMEM metadata, while `obj_sync_epoch`, ilog fetch state, pin handles, and bucket state are runtime caches. Evictable md-on-ssd pools add explicit bucket allocation and pinning to object lifetime.

## Dependencies And Integration Points
The header depends on DAOS btree/LRU APIs, VOS layout definitions, ilog handling, timestamp sets, containers, and pool internals. It is consumed by object cache, object index, object iteration/update logic, aggregation, discard, and tests that inspect object-index sanity.

## Risks
Because this header defines ownership contracts, misuse can cause leaked container references, stale durable pointers, unbalanced LRU references, or concurrent discard/aggregation conflicts. The bitfield state around bucket allocation/loading is especially sensitive to missing condition broadcasts.

## Test Signals
Tests should validate cache create/destroy, negative-to-durable object incarnation, release flag clearing, visible/non-visible hold semantics, delete/evict behavior, and md-on-ssd bucket pin/unpin behavior.
