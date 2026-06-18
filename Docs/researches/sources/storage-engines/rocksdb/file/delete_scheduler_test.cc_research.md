# sources/storage-engines/rocksdb/file/delete_scheduler_test.cc

## Purpose
`delete_scheduler_test.cc` verifies `DeleteScheduler` behavior across rate limiting, concurrency, trash naming, background failures, partial deletion, hard links, foreground fallback, accounted/unaccounted files, and bucket waits.

## Important APIs and control flow
The fixture creates three per-thread test directories, owns an `SstFileManagerImpl`, obtains its `DeleteScheduler`, and has helpers for creating tracked/untracked dummy files and counting normal/trash files. Sync points are used extensively to hold the background thread, inspect penalties, inject ordering, and count delete/ftruncate/fsync paths.

Tests cover basic rate limiting with expected cumulative penalties and directory fsync, multi-directory scheduling, multithreaded queueing, disabled rate limiting with immediate delete, trash-name conflicts, externally deleted trash files producing background errors, repeated queue draining, chunked partial deletion, hard-link fallback, destructor with non-empty queue, immediate delete when trash exceeds a configured DB-size ratio, suffix classification, mixed accounted/unaccounted file deletion, concurrent unaccounted bucket deletion, immediate unaccounted deletion with remaining links, and a regression ensuring `WaitForEmptyTrashBucket()` is signaled when a single-file bucket empties while global pending work remains.

## State, persistence, and integration
The tests operate on real default `Env` filesystem directories and use SFM accounting/statistics. They integrate with RocksDB `SyncPoint`, `Statistics` tickers (`FILES_MARKED_TRASH`, `FILES_DELETED_FROM_TRASH_QUEUE`, `FILES_DELETED_IMMEDIATELY`), hard-link APIs, and background thread timing.

## Risks and test signals
Timing-based assertions can be sensitive to slow systems, though sync points reduce nondeterminism. Some tests are Linux-conditional or disabled. The bucket-signal regression is important because a missed condition-variable signal can hang callers indefinitely. Passing this suite signals queue accounting, rate calculations, bucket counters, partial deletion, stats, hard-link policy, foreground fallback, and background error paths are working.
