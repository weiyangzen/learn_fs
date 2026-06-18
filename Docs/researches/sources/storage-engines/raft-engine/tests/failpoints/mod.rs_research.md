# sources/storage-engines/raft-engine/tests/failpoints/mod.rs

Purpose: this file is the module root for failpoint-driven integration tests and contains one local regression test for log-batch full behavior.

Important APIs and types: it enables `allocator_api` under the `swap` feature, declares helper and test modules (`util`, `test_engine`, `test_io_error`), initializes logging with a ctor, imports `FailGuard` and raft-engine public APIs, and defines `test_log_batch_full`.

Control flow: `init` runs before tests and initializes `env_logger`. `test_log_batch_full` enables failpoint `log_batch::1kb_entries_size_per_batch`, builds two batches with 800-byte entries, verifies merging two full-ish batches returns `Error::Full` without mutating either original clone, then verifies adding entries to a full clone also returns `Error::Full` without partial mutation.

State and persistence behavior: failpoint guards are scoped to the test and removed on drop. The test only manipulates in-memory `LogBatch` values. Logger initialization is process-global.

Dependencies and integration points: integrates with failpoint-enabled engine tests in sibling modules, local failpoint utilities, `LogBatch`, raft entry generation helpers, and error matching. The `swap` cfg attr allows failpoint tests to compile when allocator-api-backed swap support is enabled.

Risks and invariants: because logging initialization is global, duplicate initialization would panic if another test root did the same without guarding; this file assumes the ctor setup is acceptable for this test binary. The full-batch test asserts transactional behavior: failed merge/add must leave both source and destination batches unchanged.

Test signals: this module's explicit signal is the `test_log_batch_full` regression. The broader file also wires failpoint integration suites for engine and I/O error behavior.
