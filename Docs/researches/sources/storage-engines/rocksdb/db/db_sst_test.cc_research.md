# sources/storage-engines/rocksdb/db/db_sst_test.cc

## Purpose

This file tests SST/WAL file lifecycle behavior around creation, deletion, trash scheduling, `SstFileManager` accounting, blob-file tracking, maximum-space enforcement, compaction cancellation, table-reader opening, and total SST size properties. It focuses on persistence side effects and storage accounting more than key/value semantics.

## Important APIs, Types, And Functions

- `DBSSTTest` derives from `DBTestBase` with fsync enabled.
- `FlushedFileCollector` is an `EventListener` that records flushed file paths for later manual `CompactFiles` calls.
- `SstFileManager`, `SstFileManagerImpl`, and `DeleteScheduler` are central to tracking file sizes, delete rates, trash ratios, and background deletion.
- Tests use `OnFileDeletionListener`, `SyncPoint`, `MockEnv` time controls, `FaultInjectionTestFS`, `NewCompositeEnv`, blob-file APIs, `GetAllDataFiles`, `GetBlobFileNumbers`, `GetLiveFilesMetaData`, and `rocksdb.total-sst-files-size`.
- Parameterized fixtures cover rate-limited delete with separate WAL dirs and obsolete deletion `max_trash_db_ratio` settings.

## Control Flow

Early tests guard file deletion correctness: pending compaction outputs must not be purged while being written, `.sst` files renamed to `.ldb` must still reopen and read, moved files from move compaction must not be deleted, and obsolete files blocked by `pending_outputs_` must be retried later. Empty flushes must not create phantom SST deletion events, while non-empty flushes create one live file without deletion.

`DBWithSstFileManager` and blob variants create many SST/blob files, flush and compact, compare `SstFileManagerImpl::GetTrackedFiles()` and `GetTotalSize()` with filesystem scans, then close/reopen or destroy the DB to verify tracking is repopulated and untracked correctly. Blob GC and atomic flush tests assert blob files are added, scheduled, deleted, or preserved according to garbage-collection cutoffs and atomic flush behavior.

Rate-limited deletion tests set delete rates, use SyncPoints to observe penalty sleeps, compact files into trash, wait for empty trash, and validate `FILES_MARKED_TRASH` versus `FILES_DELETED_IMMEDIATELY`. WAL trash cleanup tests create or preserve `.log.trash` files across reopen and ensure they are removed. Obsolete deletion-on-open tests seed `.sst.trash` and obsolete SST files before open and verify background deletion policy under different trash ratios.

Space-limit and cancellation tests set `SstFileManager::SetMaxAllowedSpaceUsage`, then cause flushes or compactions to exceed the limit. They verify failed flushes, blob cleanup after failed flushes, automatic and manual compaction cancellation, `COMPACTION_CANCELLED`, and that reserved compaction size returns to zero. The randomized test keeps writing until the configured space limit is exceeded via both flush and compaction paths.

Open and size-property tests exercise `max_open_files = -1`, multi-threaded file opening, table-reader cache memory charging failures, and `rocksdb.total-sst-files-size` across live files, obsolete-but-version-pinned files, trivial moves, iterator-held versions, deletes, and compactions. The final fault-injection test verifies fallback/error behavior when SST file-size queries fail through random-access or filesystem APIs.

## State And Persistence Behavior

The file creates real SST, WAL, blob, trash, obsolete, and multi-path DB files. It intentionally closes and reopens DBs to test recovery-time tracking and cleanup. Iterator-held versions pin obsolete files and influence `total-sst-files-size`. DeleteScheduler may rename files into trash and delete asynchronously; tests frequently call `WaitForEmptyTrash`, `TEST_WaitForCompact`, `TEST_WaitForFlushMemTable`, and `TEST_WaitForPurge` to synchronize persistent side effects.

## Dependencies And Integration Points

The tests integrate with compaction, flush jobs, blob GC, file manager accounting, DeleteScheduler, table cache/table readers, cache capacity enforcement, filesystem wrappers, DB properties, DB destruction, WAL directory handling, and RocksDB statistics. They depend on `SyncPoint` names in flush, compaction, build-table, delete-scheduler, and SstFileManager internals.

## Risks And Edge Cases

These tests are timing- and filesystem-sensitive. Rate-limited deletion uses mocked time and SyncPoints to make expected penalties deterministic. File-size and total-size checks assume stable table property encoding in some cases, with an explicit workaround for oldest-key-time. Trash ratio heuristics can route files to immediate deletion or background deletion. Encrypted environments alter file-size fallback behavior. Space-limit tests intentionally trigger background errors and cancellation paths that can be affected by compaction scheduling changes.

## Test Signals

Signals include `FilesPerLevel`, live-file metadata counts and sizes, filesystem existence checks, deletion listener counts, SyncPoint counters, `SstFileManager` tracked file maps and totals, delete-scheduler trash size, statistics tickers, `IsCompactionTooLarge`, `IsMemoryLimit`, exact DB property values, and successful reads after reopen or fault injection.
