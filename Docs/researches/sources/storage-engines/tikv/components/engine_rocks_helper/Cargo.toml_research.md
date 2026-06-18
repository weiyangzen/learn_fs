<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks_helper/Cargo.toml -->
# sources/storage-engines/tikv/components/engine_rocks_helper/Cargo.toml

## Purpose
This manifest defines the `engine_rocks_helper` crate, a non-published helper crate for RocksDB-specific operational helpers around TiKV's `engine_rocks`.

## Important APIs, Types, and Functions
The crate enables an optional `failpoints` feature forwarding to `fail/failpoints`. Runtime dependencies include `engine_rocks`, `engine_traits`, `raftstore`, `keys`, `tikv_util`, Prometheus, slog, lazy_static, and fail. Dev dependencies include `kvproto` and `tempfile`.

## Control Flow
The manifest participates in Cargo feature/dependency resolution only. It exposes helper modules declared in `src/lib.rs`.

## State and Persistence Behavior
No runtime state is defined here. Dependency choices enable helper code that can inspect RocksDB live files, update raftstore `StoreMeta`, emit metrics, and panic-mark on unrecoverable SST corruption.

## Dependencies and Integration Points
The dependency on `raftstore` is significant: `sst_recovery.rs` reaches into store metadata to mark damaged regions. Prometheus supports helper metrics in `metric.rs`.

## Risks and Edge Cases
Because the crate is `publish = false`, it is intended for workspace-internal use. Feature alignment matters: failpoints in helper tests or recovery paths require the `failpoints` feature.

## Test Signals
Cargo-level validation is through workspace builds and `engine_rocks_helper` tests, especially the SST recovery test using temporary RocksDB state.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks_helper/Cargo.toml -->
