# sources/storage-engines/tikv/components/test_raftstore/Cargo.toml

Purpose: this manifest defines the legacy `test_raftstore` internal test-support crate. It is not published and provides the shared v1 harness and helper APIs used directly by tests and indirectly by the raftstore-v2 harness.

Important APIs, types, and functions: the manifest does not define code APIs, but its feature flags select engine backends. Defaults enable `test-engine-kv-rocksdb` and `test-engine-raft-raft-engine` through the `raftstore` crate. Additional feature groups expose `test-engines-rocksdb` and `test-engines-panic`.

Control flow: Cargo resolves this crate as edition 2018 with workspace dependencies for TiKV internals. Feature flags are propagated to `raftstore`, making the test harness compile against selected test engine combinations.

State and persistence behavior: none directly, but dependencies enable RocksDB, raft engine, hybrid/in-memory engines, encryption, import, resource control, resolved-ts, and TiKV server/storage components that create real temp on-disk state during tests.

Dependencies and integration points: the dependency list is intentionally broad: `raftstore` with `testexport`, `tikv`, `test_pd_client`, `engine_rocks`, `engine_test`, `engine_traits`, `kvproto`, `pd_client`, `resource_metering`, `service`, `security`, `grpcio`, `tokio`, and transaction/types crates. This breadth shows `test_raftstore` is the cross-layer test facade rather than a small unit-test helper.

Risks and test signals: changes to defaults can silently move tests to different engines. Removing a dependency may break re-exported helpers even when the manifest appears over-broad. Because `test_raftstore-v2` imports many items from this crate, dependency or feature changes here can affect both legacy and v2 test harnesses.
