# sources/object-store/daos/src/vos/vos_pool.c

## Purpose
`vos_pool.c` implements VOS pool lifecycle and metadata storage integration: pool create/open/close/destroy, PMEM/BMEM/BIO metadata context setup, WAL operations, checkpointing, pool hash/ref management, telemetry, VEA loading, GC integration, pool query/control, and feature checks.

## Important APIs, Types, And Functions
Major exports include `vos_store_ops`, `vos_pool_create_ex`, `vos_pool_create`, `vos_pool_kill`, `vos_pool_destroy_ex`, `vos_pool_open_metrics`, `vos_pool_open`, `vos_pool_upgrade`, `vos_pool_close`, `vos_pool_query`, `vos_pool_query_space`, `vos_pool_space_sys_set`, `vos_pool_ctl`, `vos_pool_checkpoint_*`, `vos_pool_biov2addr`, and compatibility flag helpers. Internal helpers cover metadata read/write/load/flush, waitqueues, WAL reserve/commit/replay/id compare, pool allocation/hash lookup, BIO blob formatting/unmap, and pool open post-processing.

## Control Flow
Pool creation validates inputs and versions, installs an opening placeholder in the UUID hash, creates an umem pool with optional BIO metadata context, initializes the root durable pool object, container table, GC state, pool extension, and optional VEA blob. Open first reuses existing handles when allowed, otherwise inserts an opening placeholder, checks BIO health, opens umem/BIO state, validates magic/version/UUID, opens the container btree, loads VEA, initializes dedup and GC, and optionally initializes checkpoint state. Close decrements opened counts, removes hash/GC refs on the final close, and frees resources when the hash link ref is dropped.

## State And Persistence
Persistent pool state includes `vos_pool_df`, `vos_pool_ext_df`, container table root, VEA metadata, pool UUID, durable version, size fields, compatibility flags, and emergency buffer. Runtime state includes pool hash links, open counts, mutex/cond for concurrent opens, umem instance, BIO contexts, VEA info, GC refs, metrics, checkpoint callbacks/context, and feature bits. WAL commits update umem cache commit IDs, and checkpointing flushes dirty metadata then advances BIO WAL checkpoint IDs.

## Dependencies And Integration Points
This file integrates with umempobj, BIO metadata/data contexts, SPDK blob/VEA, DAOS telemetry, GC, dedup, checker reporting, RAS events, VOS space accounting, pool handle hashing, and xstream-local BIO context discovery. Store ops are called by the umem layer for metadata paging, WAL, and checkpoint flushes.

## Risks
High-risk paths include error unwinding across umem and BIO context creation/open, WAL commit fatal-error handling, checkpoint callback races while `store->vos_priv` is unset, concurrent open serialization, deferred pool destroy while GC still holds refs, feature upgrade transactionality, and metadata read/load queue-depth synchronization. Non-NVMe, sysdb, external-checkpoint, RDB, and recreate flags all change behavior and need coverage.

## Test Signals
Tests should cover create/open/close/destroy across PMEM-only and BIO-backed pools, invalid magic/version/UUID checker paths, concurrent opens, exclusive/small flags, WAL reserve/commit/replay metric updates, checkpoint no-op and active paths, pool upgrade feature bits, VEA load/unmap integration, deferred destroy with open handles, and `vos_pool_ctl` parameter validation.
