# sources/object-store/daos/src/container/srv_internal.h

## Purpose
Provides private container-server declarations shared across the container service implementation. It binds together service RDB state, target-side caches, IV payload formats, metrics, epoch tracking, and cross-file function prototypes.

## Important APIs and types
- `struct cont_pool_metrics` declares per-pool container operation counters.
- `struct dsm_tls` is module TLS, containing the per-xstream `ds_cont_child` cache and open handle hash.
- `struct cont_svc` is the leader service descriptor: pool UUID/id, RDB service, lock, root/UUID/container/handle RDB paths, owning pool, and leader EC/stable epoch tracking request/list/mutex.
- `struct cont` wraps one service-side container and its RDB subpaths: property KVS, snapshots, user attrs, handle index, and OIT OID map.
- `struct cont_iv_snapshot`, `cont_iv_capa`, `cont_iv_prop`, `cont_iv_track_eph`, `cont_iv_entry`, and `cont_iv_key` define flattened IV payloads.
- Function prototypes expose service operations (`ds_cont_snap_create`, `ds_cont_prop_set`), target collectives (`ds_cont_tgt_open`, `ds_cont_tgt_destroy`), IV helpers, OID IV reservation, metrics, and OIT gathering.

## Control flow and integration
This header is the central dependency layer: service files such as `srv_epoch.c` consume `struct cont` and RDB path members, while target files such as `srv_target.c` consume TLS and IV prototypes. Container IV updates flow through declared functions like `cont_iv_prop_update()`, `cont_iv_snapshots_update()`, and `cont_iv_track_eph_update()`. Target operations declared here are invoked by service-side RPC handlers and by pool/rebuild code outside this subset.

## State and persistence behavior
The header describes both persistent RDB state (`cont_svc` and `cont` paths) and volatile per-xstream state (`dsm_tls`, target caches, handle hash). `cont_iv_prop` is a wire/cache representation of persistent properties, including checksum, redundancy, roots, status, and ACL. Epoch-tracking structures (`rank_eph`, `cont_track_eph_leader`, `cont_iv_track_eph`) bridge target-reported volatile progress to service decisions and RDB-backed EC aggregation epochs.

## Dependencies
Includes DAOS LRU, security, engine, RDB, replicated service, server container, telemetry, and the persistent layout header. It deliberately forward declares pool and container-handle types to avoid broader include coupling.

## Risks
This file is ABI-sensitive inside the module: IV payload structure changes must remain coordinated with container IV serialization and versioning. `cont_iv_prop` has `struct daos_acl` as a flexible final member, so allocation/size calculations must account for ACL length. Many functions are declared here but implemented elsewhere; mismatched assumptions about lock ownership, xstream affinity, or reference ownership can cause subtle bugs.

## Test signals
Compile coverage is important because this header cross-links many modules. Functional tests should indirectly validate IV round trips, target open/close lifecycle, property updates, snapshot refresh, OID allocation, metrics allocation count, and leader/target epoch reporting.
