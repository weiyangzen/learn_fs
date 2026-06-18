# sources/storage-engines/tikv/src/server/raftkv2/mod.rs

Purpose: implements `tikv_kv::Engine` for raftstore-v2. It routes binary simple writes, snapshots, and flashback admin commands through `raftstore_v2::RaftRouter`.

Important APIs/types/functions: `RaftKv2<EK, ER>`; `modifies_to_simple_write`; `Transform`; `async_write`; `async_snapshot`; `modify_on_kv_engine`; `exec_admin`; `raft_extension`.

Control flow: `modifies_to_simple_write` serializes puts/deletes/pessimistic locks/ranges/SST ingest into `SimpleWriteBinary`. `async_write` builds headers/flags, schedules txn-extra, freezes data for avoid-batch, subscribes to proposed/committed events, installs a before-set callback for metrics and `on_applied`, and sends `PeerMsg::SimpleWrite`. `Transform` maps v2 command events to `WriteEvent`s and emits early errors. Snapshot logic builds a Snap request with stale-read/flashback metadata and maps v2 errors or lock conflicts to KV errors.

State/persistence: raftstore-v2 owns durable apply; adapter stores only router, txn-extra scheduler, and in-memory leader set. `kv_engine()` returns `None`. Flashback admin commands persist region flashback state via raftstore-v2.

Dependencies/integration: v2 router/channel types, legacy request-header helpers, metrics, tracker, txn-extra scheduler, and v2 `Extension`. Risks include unsafe direct writes, optional future unwrap invariant in snapshots, partial parity with legacy local-engine helper surface, and known snapshot duration inaccuracy. Testing is primarily integration/failpoint-based.
