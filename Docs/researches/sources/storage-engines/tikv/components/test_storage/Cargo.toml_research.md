# Research: sources/storage-engines/tikv/components/test_storage/Cargo.toml

## sources/storage-engines/tikv/components/test_storage/Cargo.toml

Purpose: manifest for `test_storage`, a private test helper crate that wraps TiKV storage APIs with synchronous test utilities and assertions.

Features mirror `test_raftstore` engine combinations: default RocksDB KV plus raft-engine, plus optional all-RocksDB and panic-engine modes. This keeps storage tests able to switch underlying engine implementations through feature propagation to `test_raftstore`.

Dependencies identify the integration surface: `api_version`, `engine_rocks`, `engine_traits`, `kvproto`, `raftstore`, `test_raftstore`, `tikv`, `tikv_util`, `tracker`, `txn_types`, `collections`, and `futures`. The crate depends heavily on TiKV's storage command API and raftstore cluster helpers.

State and persistence are controlled by the Rust sources rather than Cargo; this manifest controls compile-time feature selection only. Risks include feature drift if `test_raftstore` feature names change, and tight coupling to internal TiKV workspace crates. Test signals are compile coverage under the different feature sets and downstream storage tests importing the reexported helper modules.
