# sources/storage-engines/tikv/components/raftstore/Cargo.toml

## Purpose
This manifest defines the `raftstore` crate package metadata, feature flags, normal dependencies, and test dependencies. The crate provides raftstore v1/shared store and coprocessor components used by TiKV and also imported by raftstore-v2 tests and workers.

## Important APIs, Types, and Functions
As a `Cargo.toml`, it has no Rust APIs. Important configuration includes:
- Package name `raftstore`, version `0.0.1`, edition 2021, unpublished.
- Default features enabling `test-engine-kv-rocksdb`, `test-engine-raft-raft-engine`, and `engine_rocks`.
- Feature flags for failpoints, test exports, RocksDB/raft-engine test engines, and panic test engines.
- Dependencies on batch-system, engine traits/Rocks, raft, raft-proto, kvproto, pd_client, resource control/metering, service, sst_importer, tikv_util, yatp, tokio, and many TiKV shared crates.
- Dev-dependencies for encryption export, engine_panic, engine_test, file_system testexport, panic_hook, and test_sst_importer.

## Control Flow
Cargo uses this manifest to resolve conditional compilation and dependency graph construction. The default feature set makes raftstore usable in tests with RocksDB-backed KV and raft-engine-backed raft storage.

## State and Persistence Behavior
The manifest does not directly manage state. It selects persistence-related implementations by enabling engine crates and test engine features. Dependency selection affects whether RocksDB compaction events, raft log storage, encryption, and SST importer behavior are compiled.

## Dependencies and Integration Points
This manifest is the integration point for raftstore's shared dependencies. In this subset, raftstore-v2 code imports raftstore store types such as `Config`, `Bucket`, `TabletSnapManager`, `Transport`, `WriterContoller`, unsafe recovery syncers, and coprocessor config/host types.

## Risks and Edge Cases
- Default test-engine features couple normal crate builds to test engine implementations unless features are customized.
- Optional `engine_rocks` is required for compaction event sender code; disabling it may affect modules behind feature gates.
- Failpoint support is opt-in through the `failpoints` feature.
- Dependency drift here can affect both raftstore v1 and raftstore-v2 shared usage.

## Test Signals
No tests are defined in the manifest, but the selected dev-dependencies and features enable the integration and failpoint test suites researched in this work item.
