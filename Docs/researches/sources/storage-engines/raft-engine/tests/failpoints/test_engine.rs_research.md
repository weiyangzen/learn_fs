<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/failpoints/test_engine.rs -->
# Research: sources/storage-engines/raft-engine/tests/failpoints/test_engine.rs

Purpose: Failpoint regression suite for Raft Engine core behavior under corrupted logs, failed purge/rewrite operations, recycling, multi-directory allocation, concurrent write grouping, listener callbacks, and sync edge cases.

Important APIs/types/functions: defines local helper `append`; tests `Engine::open`, `open_with_listeners`, `open_with_file_system`, `write`, `sync`, `fetch_entries_to`, `compact_to`, `purge_expired_files`, `purge_manager().must_rewrite_*`, `consistency_check`, `unsafe_repair`, `file_span`, `first_index`, and `last_index`. Uses `EventListener`, `FileId`, `FileBlockHandle`, `LogQueue`, `LogBatch`, `RaftLocalState`, `FailGuard`, `ObfuscatedFileSystem`, `ConcurrentWriteContext`, and `catch_unwind_silent`.

Control flow: each test builds an isolated temp directory, configures small file sizes or recovery modes, writes synthetic entries, injects failpoints at a precise storage layer, then drops and reopens the engine to validate recovery. Listener tests count log-file creation, append, memtable apply, and purge events. Rewrite tests force tiny rewrite batches and write failures through append-to-rewrite and rewrite-to-rewrite phases. Recycling tests create stale tails or simulated no-space conditions, then verify readable state and file spans after reopen.

State and persistence behavior: the suite intentionally persists log files, rewrite queues, memtables, compact markers, and recycled file metadata across engine drops. In-memory listener counters and failpoints are temporary, while the durable witness is the reopened engine's first/last indexes, fetched entries, file span, and repair/check results.

Dependencies and integration points: depends on `raft_engine::internals`, `raft_engine::env`, `kvproto::raft_serverpb::RaftLocalState`, `raft::eraftpb::Entry`, the local failpoint `util.rs` helpers, and the `fail` crate. It integrates with Raft Engine's test-only failpoints and optional `scripting` feature for `unsafe_repair`.

Risks: these tests are highly coupled to failpoint names and internal queue sequencing, so refactors can break tests without changing public API. Several assertions rely on sleeps to let paused writes reach specific phases. Some failures surface as panics because internal sync/write paths unwrap errors; this is deliberate but makes panic boundaries part of the contract. The `#[should_panic]` recycle stale-tail test documents a known issue rather than a desired success path.

Test signals: passing tests show that corrupted tails are tolerated or rejected according to recovery mode, partial rewrite failures do not lose committed entries, listeners see durable events, recycle/no-space paths remain readable, and `Engine::sync()` actually reaches the active log fsync path.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/failpoints/test_engine.rs -->
