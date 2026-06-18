<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/failpoints/test_io_error.rs -->
# Research: sources/storage-engines/raft-engine/tests/failpoints/test_io_error.rs

Purpose: Focused failpoint tests for Raft Engine I/O failures: file open/read/write/sync/rotate/truncate/allocation/no-space errors, concurrent write failures, repair failures, and recycled-file allocation gaps.

Important APIs/types/functions: exercises `Engine::open_with_file_system`, `Engine::open`, `write`, `fetch_entries_to`, `get_message`, `file_span`, `unsafe_repair_with_file_system`, `purge_expired_files`, and optional `SwappyAllocator`. Uses `ObfuscatedFileSystem`, `FailGuard`, `ConcurrentWriteContext`, `generate_batch`, `MessageExtTyped`, and `catch_unwind_silent`.

Control flow: tests create temp engines, write baseline entries, enable one or more failpoints such as `default_fs::create::err`, `log_file::read::err`, `log_file::write::err`, `log_fd::sync::err`, `log_file::truncate::err`, `log_file::allocate::err`, and `log_fd::write::no_space_err`, then assert whether the public API returns `Err`, panics, or can recover after reopen. Rotate tests run both with and without restart after each injected failure.

State and persistence behavior: the file validates that partially written data is either ignored, overwritten, or recovered consistently depending on the failure point. Durable state is checked through reopened engines, fetched entry counts, first/last indexes, directory entry counts, and file spans. Some outstanding writes are explicitly not reverted after sync panic, and the tests document that behavior.

Dependencies and integration points: integrates failpoint-controlled filesystem behavior with the real engine write group, log writer, repair, recycle prefill, spill directory selection, and optional swap allocator. It shares typed Raft-entry helpers from `util.rs`.

Risks: exact failpoint scripts depend on low-level I/O call ordering and byte-splitting behavior; using `ObfuscatedFileSystem` is avoided in one concurrent test because it would split I/O differently. Panic-vs-error expectations encode current internal unwrap choices. No-space simulations cover selected retry paths but cannot fully model real disks.

Test signals: success means expected errors do not corrupt committed state, failed followers in concurrent write groups do not poison leaders, non-atomic writes can be reopened or overwritten safely, repair failures leave original data readable, recycled-file prefill gaps are supplemented, and no-space transitions between main and spill dirs behave as intended.
<!-- END_FILE_RESEARCH: sources/storage-engines/raft-engine/tests/failpoints/test_io_error.rs -->
