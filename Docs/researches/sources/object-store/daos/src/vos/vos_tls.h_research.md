# sources/object-store/daos/src/vos/vos_tls.h

Purpose: defines per-xstream/thread VOS TLS state and inline accessors for objects that many VOS paths need without threading parameters through every call.

Important APIs/types: `struct vos_tls` holds GC pool lists, PMDK transaction-stage data, the current DTX handle, timestamp table, standalone profile, object LRU cache, pool/container handle hash tables, a saved key hash, and telemetry nodes. Accessors include `vos_pool_hhash_get`, `vos_cont_hhash_get`, `vos_obj_cache_get`, `vos_txd_get`, `vos_ts_table_get`, `vos_ts_table_set`, `vos_dth_set/get`, `vos_kh_set/get/clear`, `vos_hash_get`, and `vos_sched_seq`.

Control flow and state: most functions call `vos_tls_get(standalone)` and return fields. `vos_dth_set` also drains `dth_share_tbd_list` when replacing a DTX handle with pending shared peers. `vos_hash_get` consumes a saved hash once and otherwise computes Murmur64 with `BTR_MUR_SEED`. `vos_sched_seq` returns zero in standalone builds and the scheduler sequence otherwise.

Dependencies/integration: integrates with GURT lists/hash tables, DAOS btree/hash helpers, LRU caches, BIO xstream context, DTX server state, telemetry, VOS timestamp tables, and VOS standalone tests. Tree code uses the saved hash path to avoid recomputing hashes for long keys.

Risks: the file documents the DTX handle TLS path as a hack: callers must avoid CPU yield while relying on `vtl_dth`, or another ULT on the same xstream could change it. Hash hints are one-shot and must be cleared or consumed in the right order. Accessors assume TLS exists except for `vos_dth_get`, which tolerates null.

Test signals: cover standalone and non-standalone TLS, DTX replacement with shared peers, hash set/get/clear behavior, `vos_hash_get` consuming saved hashes, and scheduler sequence fallback under `VOS_STANDALONE`.
