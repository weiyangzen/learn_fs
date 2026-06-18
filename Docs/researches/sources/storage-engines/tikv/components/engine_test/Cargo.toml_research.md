<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_test/Cargo.toml -->
# sources/storage-engines/tikv/components/engine_test/Cargo.toml

## Purpose
This manifest defines the `engine_test` crate, a workspace-internal crate that selects concrete KV and raft engines for TiKV tests through feature flags.

## Important APIs, Types, and Functions
Default features select RocksDB for KV tests and raft-log-engine for raft tests. Feature groups include `test-engines-rocksdb` and `test-engines-panic`, plus individual `test-engine-kv-*` and `test-engine-raft-*` switches.

Dependencies include `engine_rocks`, `engine_panic`, `raft_log_engine`, `engine_traits`, `encryption`, `file_system`, and `tempfile`.

## Control Flow
Cargo feature resolution determines which concrete type aliases are exposed by `src/lib.rs` for test code. The manifest has no runtime logic.

## State and Persistence Behavior
No runtime state is stored here. Feature choices determine whether tests create RocksDB directories, raft-log-engine directories, or panic engines.

## Dependencies and Integration Points
The crate is a bridge from generic `engine_traits` tests to concrete engine implementations. Encryption and file-system rate-limiter dependencies are needed for constructor option propagation.

## Risks and Edge Cases
Multiple feature flags can select multiple implementations if cfgs are not mutually exclusive in code. Defaults matter for the whole TiKV workspace test suite, so changing them can alter storage semantics broadly.

## Test Signals
Workspace `cargo test` under default, rocksdb-only, and panic-engine feature sets validates feature compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_test/Cargo.toml -->
