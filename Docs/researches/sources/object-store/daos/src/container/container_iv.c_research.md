# sources/object-store/daos/src/container/container_iv.c

Purpose: server-side container IV cache implementation for distributing container snapshots, capabilities, properties, and tracked epoch boundaries across ranks/xstreams.

Important APIs/types/functions: IV ops `cont_iv_ops`; fetch/update helpers `cont_iv_fetch`, `cont_iv_update`; snapshot APIs `cont_iv_snapshots_fetch/update/refresh`, `ds_cont_fetch_snaps`, `ds_cont_revoke_snaps`; property APIs `cont_iv_prop_update/fetch`, `ds_cont_fetch_prop`; capability APIs `cont_iv_capability_update/invalidate`, `ds_cont_find_hdl`; epoch APIs `cont_iv_track_eph_update/refresh`, `ds_cont_fetch_ec_agg_boundary`; lifecycle `ds_cont_iv_init/fini`.

Control flow: each IV namespace entry owns a dbtree root handle storing per-container entries. Fetch checks the local tree, and if missing on the master lazily creates entries from RDB/container service state, then copies into caller buffers. Update applies local side effects such as opening/closing target container handles, refreshing target properties/snapshots, propagating tracked epoch reports to the leader, and updating the dbtree. Non-xstream-0 callers use Argobots ULT/eventual wrappers to run fetches on xstream 0.

State/persistence: IV cache is in-memory and dbtree-backed per namespace. It reflects persistent RDB/container state (`ds_cont_get_snapshots`, `ds_cont_get_prop`, handle lookup, EC aggregation boundary lookup) and pushes refreshed state into target-local container caches. Invalidation removes snapshot/property/capability/epoch entries and also invalidates OID IV entries.

Dependencies/integration: DAOS server IV layer, CART IV modes, Argobots, dbtree, pool/container server internals, security/ACL property conversion, OID IV, DTX/EC aggregation helpers.

Risks: many functions assert xstream 0, so wrong-call-context bugs can abort. Snapshot fetch uses a sentinel `snap_cnt == -1` to trigger caller buffer resize. Property IV entries require full property sets and assert required fields. Capability fetch can recurse through invalidation/retry when local handle state is stale. `cont_iv_snapshot_fetch_non_sys` assigns `snapshots = arg.snapshots` instead of `*snapshots`, which looks suspicious if caller expects the allocated pointer.

Test signals: no direct test in this subset. Tests should exercise missing-entry lazy creation, non-xstream fetch wrappers, property l2g/g2l round trips including ACLs/roots, snapshot resize sentinel, capability stale-handle recovery, and epoch report forwarding.
