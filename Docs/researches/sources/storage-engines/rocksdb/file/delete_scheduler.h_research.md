# sources/storage-engines/rocksdb/file/delete_scheduler.h

## Purpose
`delete_scheduler.h` declares the `DeleteScheduler` class, RocksDB's internal mechanism for optionally slowing file deletion through a trash queue and background worker. It documents the distinction between accounted files managed by `SstFileManager` and unaccounted files outside its size accounting.

## Important APIs and types
The constructor receives a `SystemClock`, `FileSystem`, byte-per-second rate, info log, `SstFileManagerImpl`, maximum trash/DB ratio, and maximum delete chunk size. Public methods include `GetRateBytesPerSecond()`, `SetRateBytesPerSecond()`, `DeleteFile()`, `DeleteUnaccountedFile()`, `WaitForEmptyTrash()`, `NewTrashBucket()`, `WaitForEmptyTrashBucket()`, `GetBackgroundErrors()`, `GetTotalTrashSize()`, ratio getters/setters, `IsTrashFile()`, `CleanupDirectory()`, and `SetStatisticsPtr()`.

Private helpers perform immediate deletion, queueing, trash renaming, trash-file deletion, SFM callbacks, background draining, and lazy thread creation. `FileAndDir` captures queued filename, directory to sync, accounted flag, and optional bucket.

## State, dependencies, and integration
The class depends on RocksDB `FileSystem`, `Env`, `Logger`, `SystemClock`, statistics, `InstrumentedMutex`/`InstrumentedCondVar`, and `SstFileManagerImpl`. Queue state, bucket counters, background errors, closing flag, and stats pointer are protected by `mu_`; name-conflict avoidance uses `file_move_mu_`. Atomic fields expose rate, trash size, and ratio.

## Risks and test signals
The header defines a concurrent class with strong lifecycle expectations: callers must handle remaining trash on destructor, bucket users must wait on created buckets, and SFM must outlive the scheduler. The API mixes foreground and background deletion based on rate, ratio, hard links, and force flags, so tests must cover every branch. Signals include successful wait semantics, no deadlocks, accurate stats, correct `IsTrashFile()` suffix detection, and stable behavior when rate changes from disabled to enabled.
