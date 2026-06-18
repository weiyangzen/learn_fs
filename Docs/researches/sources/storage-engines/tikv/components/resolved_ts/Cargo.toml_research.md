# sources/storage-engines/tikv/components/resolved_ts/Cargo.toml

Purpose: this manifest defines the `resolved_ts` TiKV component crate. The crate tracks transactional changes and advances per-region resolved timestamps for CDC/stale-read related subsystems.

Important APIs and types:
- Package metadata sets crate name `resolved_ts`, edition 2021, Apache-2.0 license, unpublished version `0.0.1`.
- Feature flags proxy allocator, portability, SIMD, memory profiling, failpoints, and test-engine features down to the workspace `tikv` crate.
- Integration tests are declared as `tests/integrations/mod.rs`; failpoint tests are declared separately and require the `failpoints` feature.

Dependencies:
- Core runtime dependencies include `concurrency_manager`, `engine_traits`, `pd_client`, `raftstore`, `security`, `tikv`, `tikv_util`, `txn_types`, `grpcio`, `tokio`, `futures`, `protobuf`, `kvproto`, and `prometheus`.
- The dependency set matches the source files in this subset: `advance.rs` uses PD, gRPC, tokio, security, raftstore, and concurrency manager; `cmd.rs` uses raftstore coprocessor command batches, engine CF names, kvproto raft command types, and txn type decoders.
- Dev dependencies include RocksDB/test engines, test raftstore utilities, SST importer test utilities, and tempfile.

Control flow and integration behavior:
- The crate is part of the TiKV workspace and depends on sibling workspace crates rather than standalone published versions.
- Feature flags primarily forward to the top-level `tikv` crate, so allocator/failpoint/test-engine selection remains consistent across the workspace.

State and persistence behavior:
- The manifest itself has no runtime state. It determines which resolved-ts implementation paths and tests can compile under selected features.

Risks and edge cases:
- The failpoint test target is gated; running it without `--features failpoints` will skip or fail target selection depending on the cargo command.
- Workspace dependency versions mean compatibility is coupled to the enclosing TiKV workspace, not this crate alone.

Test signals:
- The explicit `integrations` and `failpoints` test targets indicate resolved-ts has both normal integration coverage and failpoint-driven fault-path coverage.
