<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/failpoints/util.rs -->
# Research: sources/storage-engines/raft-engine/tests/failpoints/util.rs

Purpose: Shared failpoint-test utilities for Raft Engine tests, providing a typed Raft entry adapter, deterministic batch generation, silent panic capture, and a helper for forming concurrent write groups.

Important APIs/types/functions: `MessageExtTyped` implements `MessageExt<Entry = raft::eraftpb::Entry>` and returns `entry.index`. `generate_entries` builds indexed entries with optional data. `generate_batch` wraps generated entries into a `LogBatch`. `catch_unwind_silent` temporarily replaces the panic hook while running `panic::catch_unwind`. `ConcurrentWriteContext` owns an `Arc<Engine<FS>>` and spawned writer threads with `new`, `write`, `write_ext`, and `join`.

Control flow: `ConcurrentWriteContext::write_ext` installs `write_barrier::leader_exit` for the first thread, starts a no-op leader write to pause the write group, then adds follower closures that call into the same engine. `join` removes the barrier and joins all queued threads.

State and persistence behavior: helpers create in-memory batches and short-lived threads only. Persistent effects are made by the engine writes performed by callers. `catch_unwind_silent` restores the previous panic hook after the closure returns.

Dependencies and integration points: used by `test_engine.rs` and `test_io_error.rs`; depends on `raft_engine::{Engine, LogBatch, MessageExt}`, `raft::eraftpb::Entry`, `fail`, `std::sync::mpsc`, and `std::thread`.

Risks: the concurrent-write harness relies on sleeps and a specific failpoint to synchronize write groups, so it is sensitive to scheduler timing and write-barrier implementation changes. `catch_unwind_silent` mutates a process-global panic hook and should not be used around unrelated concurrent panic-sensitive tests.

Test signals: indirect signal comes from failpoint tests that use these helpers to verify batch contents, panic expectations, and concurrent write group behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/failpoints/util.rs -->
