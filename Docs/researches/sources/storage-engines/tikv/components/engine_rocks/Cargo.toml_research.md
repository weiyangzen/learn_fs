# sources/storage-engines/tikv/components/engine_rocks/Cargo.toml

Purpose: Declares the real RocksDB-backed TiKV engine crate. It exposes feature flags and dependencies for RocksDB integration, encryption, properties, raft, metrics, and test support.

Important APIs and types: Features include `trace-lifetime`, `jemalloc`, `portable`, `sse`, `failpoints`, `testexport`, and `nortcheck`. The RocksDB dependency is `tikv/rust-rocksdb` with the `encryption` feature. Edition is 2024.

Control flow and state: Cargo metadata only. Feature flags alter allocator/SIMD/runtime-check/failpoint behavior and dependency features.

Dependencies and integration: Pulls in `engine_traits`, `encryption`, `file_system`, `keys`, `kvproto`, `rocksdb`, `prometheus`, `raft`, `tikv_util`, `txn_types`, and many support crates. This crate is the concrete engine implementation behind most TiKV storage operations.

Risks: `nortcheck` disables Rust-side invariant checks and can break tests. Git-sourced RocksDB ties behavior to the external rust-rocksdb repository and its enabled `encryption` feature.

Test signals: Manifest dev-dependencies include `proptest`, `rand`, and `toml`; actual tests live in source modules.
