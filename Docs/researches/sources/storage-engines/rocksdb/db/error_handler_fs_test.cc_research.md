# sources/storage-engines/rocksdb/db/error_handler_fs_test.cc

## Purpose

This file is a RocksDB gtest suite for DB background error handling when the active `FileSystem` or `Env` reports write, read, manifest, compaction, WAL, retryable, no-space, corruption, and fenced I/O failures. It uses `FaultInjectionTestFS`, `CompositeEnvWrapper`, sync points, and listener callbacks to force failures at precise DB implementation boundaries, then verifies `Status::Severity`, manual `Resume()`, automatic retry/recovery, data visibility, WAL durability, manifest replacement, quarantine cleanup, and statistics counters.

The tests exercise both ordinary single-DB operation and multi-column-family / multi-DB interactions. Later parameterized tests specifically assert that `IOFenced` errors become fatal and cannot be cleared by `Resume()`.

## Important APIs, Types, and Functions

- `DBErrorHandlingFSTest : DBTestBase` constructs a fault-injection file system over the base test environment and exposes `GetManifestNameFromLiveFiles()` to identify the live descriptor file after recovery.
- `ErrorHandlerFSListener : EventListener` is the central test probe. It observes table creation starts, background errors, recovery begin/end notifications, can disable auto recovery, override the background error status, and inject a filesystem error after a configurable number of table-creation callbacks.
- `OnTableFileCreationStarted()` toggles the fault filesystem inactive once `file_count_` reaches zero, allowing multi-DB tests to fail during a specific SST creation.
- `OnErrorRecoveryBegin()` can set `*auto_recovery = false`, testing user listener veto of automatic recovery.
- `OnBackgroundError()` can replace the error observed by RocksDB with a test-provided `Status`, allowing compaction paths to be forced into hard/soft severity cases.
- `OnErrorRecoveryEnd()` records completion and the new background error so tests can assert successful recovery, aborted recovery, or shutdown-in-progress races.
- `WaitForRecovery()` and `WaitForTableFileCreationStarted()` use `InstrumentedMutex`/`InstrumentedCondVar` to synchronize tests with asynchronous recovery and table creation.
- The suite uses `SyncPoint::SetCallBack`, `LoadDependency`, `TEST_SYNC_POINT`, and named production sync points such as `BuildTable:BeforeFinishBuildTable`, `VersionSet::LogAndApply:WriteManifest`, `WritableFileWriter::Append:BeforePrepareWrite`, and `NotifyOnErrorRecoveryEnd:MutexUnlocked:*`.

## Control Flow and Test Coverage

Early flush tests inject errors around SST build lifecycle points. `FlushWriteError` and `FlushWriteNoSpaceError` assert no-space flush errors become hard errors and require manual `Resume()`. `FlushWriteRetryableError` checks retryable generic I/O failures at finish, sync, and close table-file points become soft errors. `FlushWriteFileScopeError` verifies file-scoped data-loss errors are also treated as soft/recoverable for table output failure scenarios.

WAL/flush interactions are split by WAL settings. `FlushWALWriteRetryableError` and `FlushWALAtomicWriteRetryableError` inject failure while syncing closed WALs and expect hard errors even when the underlying status is retryable. The no-WAL flush tests verify soft severity and continued in-memory write/read behavior when `WriteOptions::disableWAL` is true.

Manifest tests inject failures in `VersionSet::LogAndApply:WriteManifest`. They verify hard/no-space, retryable, file-scope, no-WAL retryable, and double-failure behavior. Successful recovery must produce a different live manifest and clear `TEST_GetFilesToQuarantine()`, preserving keys across reopen. `DoubleManifestWriteError` deliberately fails the first recovery `Resume()` and then succeeds after callbacks are cleared.

Compaction tests cover manifest append failures and output-file failures in background compaction. Sync-point dependencies force compaction to reach the failing state while foreground flush operations proceed. The suite checks soft retryable errors, hard overrides, disabled flaky variants for retryable/file-scope compaction write errors, and unrecoverable corruption. Compaction recovery cases verify rescheduling and eventual successful compaction.

WAL write tests inject append failures after partial successful WAL writes. They assert corrupted second batches are not visible or recovered, earlier synced batches remain durable, and later writes after `Resume()` or auto-recovery are durable. Multi-CF WAL tests ensure all column families flush consistent state after recovery.

Multi-DB tests share an `SstFileManager` and a default `FaultInjectionTestEnv` across three DB instances. Per-DB `FaultInjectionTestFS` wrappers simulate different failure timing. The tests verify that one DB can soft-recover, one can hard-recover, and another can proceed without error while shared file-manager state remains closeable.

Auto-recovery tests configure `max_bgerror_resume_count` and `bgerror_resume_retry_interval`, then coordinate retry loops with sync points. They cover successful and failed auto recovery for no-WAL flush, normal flush, manifest writes, compaction manifest writes, compaction output writes, WAL append failures, aborted recovery after retry exhaustion, and races between recovery threads and DB destruction.

Read-error tests inject retryable read-like validation failures in `BuildTable:BeforeOutputValidation` and compaction read points. They validate that the background error is cleared after auto recovery, counters are incremented, and data remains available after reopen. Atomic flush variants cover multi-CF atomic flush read/no-space failures.

The parameterized `DBErrorHandlingFencingTest` runs under both `paranoid_checks` values and covers flush, manifest, compaction, and WAL `IOFenced` failures. Each asserts fatal severity, `IsIOFenced()`, and that subsequent `Resume()` or writes remain fenced rather than clearing the fatal state.

## State and Persistence Behavior

The tests deliberately transition the DB through active, background-error, recovery-in-progress, resumed, closed, destroyed, and reopened states. Persistence expectations are explicit: data flushed before an error must survive reopen; data from partially failed WAL batches must not become visible; no-WAL writes remain visible in memory through soft flush failure and are persisted after recovery/flush; manifest recovery replaces the descriptor file and empties quarantine state.

The fixture-level `FaultInjectionTestFS` controls filesystem activity and error status. Several tests disable the FS until a production path hits the failing sync point, then reactivate it before manual resume or auto-recovery. The listener tracks `new_bg_error_` to distinguish successful recovery (`OK`), aborted recovery, shutdown-in-progress, and unrecoverable/fatal errors.

Statistics counters are a persistence-adjacent signal for DB error-handler state transitions: `ERROR_HANDLER_BG_ERROR_COUNT`, `ERROR_HANDLER_BG_IO_ERROR_COUNT`, `ERROR_HANDLER_BG_RETRYABLE_IO_ERROR_COUNT`, `ERROR_HANDLER_AUTORESUME_COUNT`, retry totals, success counts, and the auto-resume retry histogram are asserted in selected tests.

## Dependencies and Integration Points

This test file integrates with `DBTestBase`, `DBImpl` test-only methods (`TEST_GetBGError`, `TEST_GetFilesToQuarantine`, `TEST_WaitForCompact`), `SstFileManagerImpl`, `FaultInjectionTestFS`, `FaultInjectionTestEnv`, RocksDB listeners, `IOStatus` metadata (`SetRetryable`, `SetScope`, `SetDataLoss`, `IOFenced`), and the sync-point test framework.

The production integration points under test include flush jobs, table building and validation, WAL append/sync paths, manifest log-and-apply, compaction scheduling/output, auto-recovery loops, error listener notification in `EventHelpers`, and DB destruction/close coordination with recovery threads.

## Risks and Maintenance Notes

The suite is highly timing-sensitive. Many tests depend on exact sync-point names inside production code; refactors that rename or move sync points can silently invalidate intended failure timing. Tests that sleep via retry intervals or wait for asynchronous recovery can be slow or flaky on constrained environments.

Several tests skip under `mem_env_` because real filesystem behavior is required. Disabled compaction write retryable/file-scope tests signal known instability or incomplete coverage in those scenarios.

There are typo-like test names (`FlushWrit...`, `fromt`, `cleand`, `sucessful`) that do not affect behavior but can complicate searching. Manual ownership appears in multi-DB tests (`new FaultInjectionTestEnv`, raw `FaultInjectionTestFS*`, explicit `delete def_env`), so cleanup paths must stay exception/assert-safe enough for gtest process semantics.

Fencing tests encode a strong contract: once `IOFenced` is observed, recovery must not downgrade it. Changes to error severity mapping must preserve this fatal behavior.

## Test Signals

The file itself is test coverage. It should be run via the RocksDB gtest target for `error_handler_fs_test` on a non-mock filesystem environment. Passing signals include expected status severities, successful/manual `Resume()` outcomes, recovery listener notifications, stable post-reopen reads, manifest replacement, quarantine cleanup, expected L0/L1 file counts after compaction, and precise error-handler statistic counters.
