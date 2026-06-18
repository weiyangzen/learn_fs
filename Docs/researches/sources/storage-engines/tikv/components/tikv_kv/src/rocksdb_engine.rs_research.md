# sources/storage-engines/tikv/components/tikv_kv/src/rocksdb_engine.rs

Purpose: implements a testing-only `RocksEngine` backed by `engine_rocks::RocksEngine`, with asynchronous write/snapshot behavior simulated through a TiKV worker.

Important APIs: `RocksEngine::new()` opens RocksDB, optionally in a temp dir, and starts an `engine-rocksdb` worker. `with_raft_extension()` swaps the raft extension type. Test controls include `trigger_not_leader()`, `pause()`, `stop()`, `register_observer()`, region info provider setters, and direct accessors for underlying engines. The `Engine` impl exposes Rocks snapshots, local RocksDB, async writes, async snapshots, local modify application, and region seek.

Control flow: `Task::{Write, Snapshot, Pause}` is run by `Runner`. `async_write()` validates failpoints/empty batches, runs `pre_propose()` through coprocessor observers by converting modifies to raft requests and back, sends subscribed proposed/committed events, schedules a worker write, and emits `Finished` from the callback after optional `on_applied`. `async_snapshot()` schedules a snapshot oneshot on the worker and returns the resulting `Arc<RocksSnapshot>`.

State and persistence: RocksDB stores the actual data. Shared engine state includes worker/core lifetime, scheduler, cloned `Engines`, `not_leader` atomic, coprocessor host, optional region info provider, and raft extension. Dropping the core stops the worker and a temp dir is retained for memory-mode cleanup.

Dependencies and integration: integrates `engine_rocks`, `engine_traits`, `file_system::IoRateLimiter`, `raftstore` coprocessor/region provider APIs, `futures` streams/channels, `tikv_util::worker`, and the crate `write_modifies()`.

Risks: intended only for tests; `pre_propose()` uses a synthetic region id 1; stream events are sent with `try_send`, so event delivery can be dropped if capacity logic is wrong; `async_snapshot()` unwraps the oneshot result after scheduling; not-leader state is sticky once triggered. SST ingest remains unsupported in local write path.

Test signals: no local tests, but this engine backs the shared engine tests in `lib.rs` and is covered indirectly by test suites using Rocks-backed mock/local engines and failpoints.
