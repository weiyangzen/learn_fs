# sources/storage-engines/tikv/components/raft_log_engine/src/lib.rs

Purpose: Defines the public crate boundary for the raft-log-engine adapter. It explains that the crate implements `engine_traits` for `raft_engine` and re-exports the main adapter types.

Important APIs/types/functions: The file enables `feature(test)` under tests, imports TiKV utility macros, declares `mod engine` and `mod perf_context`, and publicly re-exports `ManagedFileSystem`, `RaftEngineConfig`, `RaftLogBatch`, `RaftLogEngine`, `ReadableSize`, and `RecoveryMode`.

Control flow: There is no runtime control flow. Module declarations compile implementation files, and re-exports define what downstream crates can name directly.

State and persistence behavior: State behavior is delegated to `engine.rs`; this file only shapes the public API.

Dependencies and integration points: Downstream raftstore code imports `RaftLogEngine` and config types from this crate rather than from `raft_engine` directly. The documentation also sets a naming convention, though the current exported type is `RaftLogEngine`, not a Rocks-style name.

Risks: Public re-export changes would ripple through TiKV storage code. The crate-level documentation notes work-in-progress abstraction, so trait/API churn should be expected carefully.

Test signals: Compile tests validate exports. Functional tests live in `engine.rs` and higher-level raftstore integration tests.
