# sources/storage-engines/tikv/components/raft_log_engine/Cargo.toml

Purpose: Defines the `raft_log_engine` crate, TiKV's adapter from the external `raft-engine` crate to TiKV's `engine_traits::RaftEngine` interfaces.

Important APIs/types/functions: The manifest declares a single feature, `failpoints`, forwarding to `raft-engine/failpoints`. Dependencies include `codec`, `encryption`, `engine_traits`, `file_system`, `kvproto`, `raft`, `raft-engine`, logging utilities, `tikv_util`, and `tracker`. `tempfile` is used for tests.

Control flow: Cargo feature selection can enable raft-engine failpoints for testing. The library exports are configured in `src/lib.rs` and implemented primarily in `src/engine.rs`.

State and persistence behavior: The crate's runtime persistence is raft log/state data in raft-engine files. The manifest itself does not configure persistence paths; callers pass `RaftEngineConfig` at runtime.

Dependencies and integration points: It is the bridge between TiKV raftstore code and `raft-engine`, with encryption and I/O rate limiting support. `engine_traits` makes it interchangeable with other raft engine implementations in generic raftstore code.

Risks: Dependency versions and trait contracts are central; mismatches between `raft-engine` and TiKV `engine_traits` can break raft persistence semantics. Failpoint feature exposure should remain test-only.

Test signals: `tempfile` supports local engine tests in `engine.rs`; feature testing should include failpoints where raft-engine failpoint behavior is expected.
