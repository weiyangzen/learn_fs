# sources/storage-engines/tikv/components/tikv_kv/src/raft_extension.rs

Purpose: defines an optional extension trait for code that normally works through `Engine` but occasionally needs direct raftstore operations, such as feeding raft messages, reporting unreachable peers, splitting regions, querying region metadata, or checking consistency.

Important APIs: `RaftExtension` is `Clone + Send` and supplies default no-op reporting methods plus async `split`, `query_region`, and `check_consistency` methods returning boxed futures. `FakeExtension` is the default implementation and supports no raft operations.

Control flow: all methods are default trait methods. Reporting hooks return immediately. Async operations return futures that resolve to unsupported errors unless a concrete raft-backed engine overrides them.

State and persistence: no local state. Implementors are expected to bridge to raftstore state, peer routing, region metadata, and snapshot status tracking.

Dependencies and integration: uses `kvproto` region/message protobufs, `raft::SnapshotStatus`, `raftstore::store::region_meta::RegionMeta`, and the crate `Result`. `Engine::RaftExtension` in `lib.rs` defaults to `FakeExtension`, while `RocksEngine` can be parameterized with a custom extension for testing.

Risks: default no-op methods can silently drop raft signals if a caller assumes a real extension. Unsupported async operations surface as runtime errors rather than compile-time capability checks.

Test signals: no local tests; validation comes from concrete raftstore integrations and tests that inject non-fake extensions.
