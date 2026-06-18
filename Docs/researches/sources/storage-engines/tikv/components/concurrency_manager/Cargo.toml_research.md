# sources/storage-engines/tikv/components/concurrency_manager/Cargo.toml

Purpose: package manifest for TiKV’s `concurrency_manager` crate, which provides in-memory transaction lock checking and max-ts tracking.

Important APIs and types: declares crate metadata, dependencies, dev-dependencies, and two Criterion benchmark targets: `lock_table` and `update_max_ts`.

Control flow: no runtime control flow. Build behavior is shaped by dependencies: `tokio` with macros/sync/time, `crossbeam-skiplist`, `pd_client`, `txn_types`, `prometheus`, `fail`, `mockall`, and TiKV utility crates.

State and persistence: none directly; dependency selection implies all state is in-memory and metrics-based rather than on-disk.

Dependencies and integration: `crossbeam-skiplist` backs the lock table; `pd_client` supplies TSO; `txn_types` supplies keys, locks, and timestamps; `prometheus` exports gauges; `tikv_alloc` with jemalloc is available only in dev tests for memory usage.

Risks: `mockall` is a normal dependency rather than dev-only because `#[automock]` appears in library code. The crate is unpublished and workspace-bound, so versioning is internal. Benchmarks require `harness = false`.

Test signals: dev dependencies support Criterion benches, futures executor for blocking tests/benches, random workload generation, and allocator statistics for ignored memory tests.
