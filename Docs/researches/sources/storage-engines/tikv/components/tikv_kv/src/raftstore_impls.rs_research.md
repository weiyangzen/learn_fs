# sources/storage-engines/tikv/components/tikv_kv/src/raftstore_impls.rs

Purpose: adapts raftstore `RegionSnapshot` and `RegionIterator` into the `tikv_kv` `Snapshot`, `SnapshotExt`, and `Iterator` traits, preserving region bounds and raft transaction metadata for upper KV layers.

Important APIs: `RegionSnapshotExt` exposes data version, max-ts sync state, raft term, region id, transaction extra op, `TxnExt`, bucket metadata, and in-memory-engine hit information. `impl EngineSnapshot for RegionSnapshot<S>` provides `get`, `get_cf`, `get_cf_opt`, `iter`, lower/upper bounds, and `ext`. `impl EngineIterator for RegionIterator<S>` forwards movement and access methods and validates keys through `should_seekable`.

Control flow: snapshot reads and iterator seeks delegate directly to raftstore objects, mapping raftstore errors into `tikv_kv::Error`. Several failpoints inject errors for snapshot get/get_cf/iter and iterator seek paths.

State and persistence: no owned persistent state; all data is borrowed or delegated from the underlying `RegionSnapshot<S>`, including region bounds, transaction metadata, and bucket info.

Dependencies and integration: connects `engine_traits::Snapshot` to `tikv_kv::Snapshot`, `raftstore::store::{RegionSnapshot, RegionIterator, TxnExt}`, `pd_client::BucketMeta`, `kvproto::ExtraOp`, and `txn_types` keys/values. This is the bridge that makes raft-region snapshots usable by the generic KV read path.

Risks: `is_max_ts_synced()` returns false when `txn_ext` is absent, which is stricter than the default `SnapshotExt`; callers must handle region-bounded lower/upper limits. Key validation is essential to prevent out-of-region seeks.

Test signals: no direct tests; failpoints are designed for raftkv tests, and behavior is covered where raftstore snapshots are read through the `tikv_kv` abstraction.
