# sources/storage-engines/badger/batch_test.go

Purpose: verifies `WriteBatch` behavior under large write volume, deletes, empty batches, repeated flush/cancel, and managed-mode error paths.

Important tests: `TestWriteBatch` writes 50,000 keys and deletes 1,000, then iterates to confirm remaining keys/values. It runs disk mode and skips in-memory mode with a TODO. `TestEmptyWriteBatch` confirms empty flushes do not deadlock in normal and managed variants. `TestFlushPanic` checks flush after flush and flush after cancel return `y.ErrCommitAfterFinish`. `TestBatchErrDeadlock` checks a managed write batch with timestamp 0 returns an error rather than deadlocking.

State and persistence: tests create temp DBs and exercise on-disk write path; value threshold is lowered to avoid too many open files. Dependencies are Badger test helpers, `require`, and internal `y` errors. Risks: skipped in-memory mode leaves a known coverage gap; high-volume test can be slow or file-descriptor sensitive. Test signals are good for lifecycle and deadlock regressions, weaker for async callback error ordering and throttle resizing.
