# sources/object-store/daos/src/container/oid_iv.c

Purpose: server-side IV cache for reserving object ID ranges per container and pool.

Important APIs/types/functions: structs `oid_iv_key`, `oid_iv_entry`, `oid_iv_priv`; IV callbacks `oid_iv_key_cmp`, `oid_iv_ent_update`, `oid_iv_ent_refresh`, `oid_iv_ent_get/put/init/destroy`, `oid_iv_alloc`; exported `oid_iv_reserve`, `oid_iv_invalidate`, `ds_oid_iv_init`, and `ds_oid_iv_fini`.

Control flow: callers pass an `oid_iv_range` in an SGL to `oid_iv_reserve`. The IV update callback locks the per-entry mutex, satisfies requests from locally cached available IDs when possible, or forwards to the root/master. On the master, it calls `ds_cont_oid_fetch_add` to atomically advance persistent max OID. If forwarded, refresh updates local available range, reserves the originally requested count, writes the returned start OID into the caller's range, and unlocks.

State/persistence: local IV entries cache a range (`oid`, `num_oids`) plus current request identity to detect duplicate callbacks while locked. Persistent OID high-water state is updated only at the master through container service storage. Invalidations mark/delete the IV entry for a pool/container key.

Dependencies/integration: DAOS server IV framework, Argobots mutexes, container service `ds_cont_oid_fetch_add`, pool/container UUID keys, and `oid_iv_range`.

Risks: lock release is split across update and refresh for forwarded requests, so callback pairing is critical. `oid_iv_ent_fetch` asserts unreachable. Allocation batching uses `OID_BLOCK` and can over-reserve to reduce root traffic. Busy duplicate handling depends on `req_rank` and `req_ptr` identity.

Test signals: no direct test in this subset. Useful tests should cover local cached allocation, root fetch-add path, forwarded refresh, duplicate request handling, invalidation, and concurrent reservation contention.
