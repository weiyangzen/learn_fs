# sources/storage-engines/tikv/components/backup/Cargo.toml

## Purpose
This manifest defines the TiKV `backup` component crate. It is an unpublished Rust 2021 crate that implements backup endpoint/service behavior, disk snapshot backup support, writers, metrics, errors, and utility code used by TiKV backup/BR paths.

## Important APIs, Types, And Functions
The manifest exposes feature wiring rather than Rust APIs. Default features enable RocksDB KV test engine and raft-engine test engine support through the workspace `tikv` crate. Additional features forward allocator, CPU portability/SSE, memory profiling, failpoint, and alternate test-engine selections to `tikv`.

## Control Flow
There is no runtime control flow in the manifest. Build-time behavior is controlled by feature selection. The crate depends on many workspace components and a few external crates; dev-dependencies add `rand`, `tempfile`, and Tokio test/time/macros.

## State And Persistence Behavior
The manifest controls which storage, encryption, and external-storage dependencies are compiled. It does not persist state itself, but its dependency graph enables backup code to interact with RocksDB engines, external storage backends, encryption metadata, Prometheus metrics, and Tokio runtimes.

## Dependencies And Integration Points
Key dependencies include `api_version`, `causal_ts`, `concurrency_manager`, `engine_traits`, `engine_rocks`, `external_storage`, `file_system`, `grpcio`, `kvproto`, `raftstore`, `resource_control`, `tikv`, `tikv_util`, `txn_types`, `tokio`, `prometheus`, and `thiserror`. This positions the crate at the integration point between BR RPCs, TiKV storage engines, raftstore region metadata, resource control, encryption, and object/local storage backends.

## Risks And Edge Cases
Feature forwarding means changes in workspace `tikv` feature names can break this crate. The default feature set is test-engine oriented, which is useful for component tests but should be understood when comparing production build profiles. The crate uses nightly-only Rust features in `lib.rs`, so toolchain compatibility matters.

## Test Signals
The manifest’s dev-dependencies support the extensive unit tests embedded in `endpoint.rs` and likely other backup modules. Feature flags such as `failpoints` and test-engine selections determine which test scenarios compile.
