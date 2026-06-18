# sources/object-store/daos/src/vos/vos_obj_cache.c

## Purpose
`vos_obj_cache.c` implements the DRAM LRU cache for VOS objects, including allocation/free callbacks, object lookup, negative cache entries, md-on-ssd bucket pinning, object acquisition/release, discard/aggregation conflict checks, and multi-object pin handles.

## Important APIs, Types, And Functions
The local LRU key is `(struct vos_container *, daos_unit_oid_t)`. LRU callbacks allocate `struct vos_object`, compare keys, hash records, print keys, and free objects. Public/internal entry points include `vos_obj_cache_create`, `vos_obj_cache_destroy`, `vos_obj_cache_evict`, `vos_obj_hold`, `vos_obj_acquire`, `vos_obj_incarnate`, `vos_obj_release`, `vos_obj_evict`, `vos_obj_evict_by_oid`, `vos_obj_check_discard`, `vos_bkt_array_*`, `vos_pin_objects`, and `vos_unpin_objects`.

## Control Flow
`obj_get` holds or creates an LRU reference unless the pool is dying. `vos_obj_hold` is the legacy hold path for fetch/iteration: it may use a thread-local `obj_local` when an uncached object is loaded without create, later moving it into LRU via `cache_object`. For update/punch, `vos_obj_acquire` always creates a cache entry, then optional `vos_obj_incarnate` inside the transaction finds or allocates the durable OI record and updates ilogs. Release unpins md-on-ssd cache ranges if the LRU reference is the last user, clears discard/aggregation flags, and drops or evicts the reference.

## State And Persistence
The cache owns transient container refs, object tree handles, ilog fetch caches, local sync epoch, zombie/discard/aggregate flags, and md-on-ssd pin handles. Durable persistence occurs only through OI calls and transaction updates to fields such as phase-2 bucket IDs. Bucket allocation is coordinated outside active umem transactions and synchronized with Argobots mutex/condition variables.

## Dependencies And Integration Points
This module integrates with DAOS LRU, VOS containers/pools, object index functions, ilog timestamp tracking, umem cache pin/unpin, telemetry gauges/counters, and VOS transaction/DTX state. Aggregation and discard query `vos_obj_check_discard` before mutating an object, while scrub/query/fetch paths depend on hold/release semantics.

## Risks
High-risk areas are negative cache conversion, thread-local object cleanup, md-on-ssd bucket allocation races, unpin timing relative to LRU last-user checks, and object eviction while other references exist. `check_discard` intentionally serializes discard and aggregation broadly; changing it can introduce races between update, discard, EC aggregation, and VOS aggregation.

## Test Signals
Tests should cover cache hits/misses, negative entries, create vs non-create holds, object zombie retry, shutdown behavior, discard/aggregation conflict return codes, evict-by-oid idempotence, bucket array sorting/subset behavior, pinning multiple objects with duplicate buckets, and pin/unpin cleanup on failures.
