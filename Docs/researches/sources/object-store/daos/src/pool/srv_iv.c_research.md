# sources/object-store/daos/src/pool/srv_iv.c

## Purpose

This file implements the pool IV cache classes. It serializes and distributes pool maps, pool properties, server handles, and connected pool handles across ranks; refreshes target-local state when IV entries change; invalidates stale entries; and registers the pool IV classes with the generic DAOS IV layer.

## Important APIs, types, and functions

- Size/allocation helpers: `pool_iv_map_ent_size()`, `pool_iv_prop_ent_size()`, and `pool_iv_value_alloc_internal()`.
- Property conversion: `pool_iv_prop_l2g()` and `pool_iv_prop_g2l()`.
- Connection helpers: lookup, delete, insert, buffer merge, resize, fetch, and update helpers using `pic_size == (uint32_t)-1` as a retry sentinel.
- IV callback table: `pool_iv_ops` with init, fetch, update, refresh, invalidate, value allocation, and pre-sync behavior.
- Public APIs: map update, connection handle update/fetch/invalidate, map refresh ULT, server handle update/fetch/invalidate, property update/fetch, service-list fetch, IV init, and IV fini.

## Control flow

Updates go through `pool_iv_update()`, which creates a single-iov value, fills `struct pool_iv_key` with expected size, HLC epoch, master term, and UUID selector, then calls `ds_iv_update()`. Map fetch starts with a small expected target count and retries when a fetched result marks `pb_target_nr == (uint32_t)-1`. Connection fetch similarly retries when `pic_size == (uint32_t)-1` and the required buffer size is returned. Update and refresh callbacks apply side effects to target-local pool state, then copy into the IV cache unless the pool is stopping. Epoch checks suppress stale nonzero updates.

## State and persistence behavior

The IV cache is transient distributed state mirroring durable pool service state. This file does not write RDB records directly. It mutates in-memory pool maps, properties, connected handle state, server pool/container handles, IV namespace master rank/term, and synchronization condition variables. Durable changes originate in pool service code and are propagated through these IV APIs.

## Dependencies and integration points

It depends on the DAOS IV layer, pool-map sizing, DAOS property and ACL APIs, security credentials, HLC timestamps, Argobots synchronization, and pool service/target helpers declared in `srv_internal.h`. `srv_pool.c` produces IV updates after property/map/handle changes; target code consumes them through `ds_pool_tgt_map_update()`, `ds_pool_tgt_prop_update()`, and `ds_pool_tgt_connect()`. Container code can fetch service ranks through `ds_pool_iv_svc_fetch()`.

## Risks and test signals

`PROP_SVC_LIST_MAX_TMP` is fixed at 16 and property serialization asserts smaller service lists. The `-1` retry sentinel protocol is subtle and must not be persisted as real data. Epoch ordering can drop legitimate updates if keys are misinitialized. Tests should cover map and connection retry resizing, duplicate handle insert, handle invalidation, stale epoch suppression, not-leader and forward cases, service handle update/fetch/invalidate, ACL/service-list property round trips, stopping pools during refresh, and IV class register cleanup.
