# sources/storage-engines/rocksdb/db/column_family_test.cc

## Purpose

This file is a large GoogleTest suite for RocksDB column-family behavior. It exercises the public `DB`/`ColumnFamilyHandle` APIs and several `DBImpl`/`ColumnFamilyData` internals across create/drop/reopen flows, WAL recovery, flushing, compaction scheduling, write stalls, per-column-family paths, option validation, and user-defined timestamp retention. The suite is parameterized over block-based table format versions so many scenarios run against both the default and latest table format.

## Important APIs, Types, and Helpers

- `EnvCounter` extends `SpecialEnv` and counts `NewWritableFile()` calls. Tests use it to detect unexpected WAL/SST/OPTIONS file creation.
- `ColumnFamilyTestBase` owns the test DB lifecycle, `EnvCounter`, `DBOptions`, `ColumnFamilyOptions`, open handles, and helper methods.
- Helper methods include `Open`, `TryOpen`, `OpenReadOnly`, `Reopen`, `Close`, `Destroy`, `CreateColumnFamilies`, `DropColumnFamilies`, `Put`, `Merge`, `Flush`, `CompactAll`, `Compact`, `Get`, `PutRandomData`, `WaitForFlush`, `WaitForCompaction`, `FilesPerLevel`, `CountLiveFiles`, `CountLiveLogFiles`, and `RecalculateWriteStallConditions`.
- `FlushEmptyCFTestWithParam` adds a `(format_version, allow_2pc)` parameter pair to validate WAL/min-log behavior with and without two-phase commit.
- `ColumnFamilyRetainUDTTest` configures a timestamp-aware comparator with `persist_user_defined_timestamps=false` and wraps timestamped `Put`/`Get` plus `CheckEffectiveCutoffTime`.
- `AutoFlushRetainUDTTest` and `ManualFlushSkipRetainUDTTest` specialize UDT-retention tests for automatic and manual flush/compaction behavior.
- Local comparators (`TestComparator`, `TestTsComparator`) validate comparator plumbing and timestamp-size restrictions.

## Control Flow and State Behavior

The fixture creates an isolated per-thread DB path, destroys prior state in `SetUp`, and destroys live handles/DB contents in the destructor. Most tests follow the pattern `Open -> create CFs -> write/flush/compact/drop -> Reopen or Close -> assert recovered state`. This makes manifest state, WAL state, and live-file state explicit test outputs.

Column-family identity and persistence tests cover:

- `DontReuseColumnFamilyID`: creates and drops CFs across reopen and `WriteSnapshot()` boundaries to ensure dropped IDs are not reused.
- `AddDrop`, `BulkAddDrop`, `DropTest`, and `CreateDropAndDestroy*`: validate create/drop APIs, handle destruction, list output, file cleanup, and behavior when file deletions are disabled.
- `EmptyNameRejected`: verifies empty CF names are rejected by single and bulk creation APIs because empty string is reserved in RocksDB metadata and older behavior lost data after reopen.
- `CreateMissingColumnFamilies`: checks `create_missing_column_families` is required, works for new and existing DBs, and avoids quadratic OPTIONS-file writes.

Recovery and WAL-oriented tests cover:

- `FlushEmptyCFTest`/`FlushEmptyCFTest2`: use `FaultInjectionTestEnv` to freeze file-system state after flush/WAL transitions, then reopen to verify sequence IDs and min-log-number metadata preserve data.
- `IgnoreRecoveredLog`: copies WALs, recovers, restores old WAL copies, and reopens again to ensure already recovered logs are ignored rather than replayed twice.
- `CrashAfterFlush`: simulates unsynced data loss after a flush and verifies cross-CF write-batch atomicity after recovery.
- `LogDeletionTest`, `DifferentWriteBufferSizes`, `FlushStaleColumnFamilies`, `FlushCloseWALFiles`, `IteratorCloseWALFile*`, `ForwardIteratorCloseWALFile`, and `LogSyncConflictFlush`: assert WAL retention, closing, deletion, and sync/flush interactions under multiple CFs, immutable memtables, and iterator-held super versions.

Compaction and flush scheduling tests use `SyncPoint`, background thread blocking, and file-per-level assertions to validate concurrency:

- `DifferentCompactionStyles` sets universal compaction for one CF and leveled compaction for another, then checks separate compaction outcomes.
- `MultipleManualCompactions`, `AutomaticAndManualCompactions`, `ManualAndAutomaticCompactions`, `SameCFManualManualCompactions`, `SameCFManualAutomaticCompactions`, `SameCFManualAutomaticCompactionsLevel`, and `SameCFAutomaticManualCompactions` orchestrate manual and automatic compactions across the same or different CFs. They verify conflict handling, no data loss, and expected level layouts.
- Write stall tests manipulate `VersionStorageInfo` counters under the DB mutex and call `ColumnFamilyData::RecalculateWriteStallConditions()` to assert delayed-write rate, stopped-write state, and allowed background compaction parallelism.
- `CompactionSpeedupForCompactionDebt` and `CompactionSpeedupForMarkedFiles` test the logic that increases background compaction capacity based on compaction debt or table-property `NeedCompact()` signals.

Iterator/read tests validate API guarantees:

- `NewIteratorsTest` tests multi-CF iterator creation with normal and tailing iterators.
- `ReadOnlyDBTest` confirms read-only open requires default CF and cannot open dropped CFs.
- `ReadDroppedColumnFamily`, `LiveIteratorWithDroppedColumnFamily`, and `FlushAndDropRaceCondition` assert handles/iterators can continue reading dropped CF data until handles are destroyed.

Option and path tests cover:

- `SanitizeCfOptions`: checks trigger ordering, minimum levels, and arena block size adjustment.
- `ValidateBlobGCCutoff`, `ValidateBlobGCForceThreshold`, and `ValidateMemtableKVChecksumOption`: validate option bounds and supported values.
- `DefaultCfPathsTest` and `MultipleCFPathsTest`: verify SSTs are written to CF-specific paths or DB paths as configured and remain readable after reopen.

UDT-retention tests cover:

- Feature incompatibilities with non-u64 timestamp comparators, atomic flush, and concurrent memtable writes.
- Automatic flush behavior when `full_history_ts_low` is unset, all keys are expired, not all keys are expired but write stall is possible, or a flush should be rescheduled.
- Manual flush and manual compaction deliberately skip the auto-retention reschedule path while still advancing the effective cutoff after garbage collection.
- Flush GC removes stale point and range-deletion entries and updates table properties.
- External SST ingestion in UDT mode rejects overlapping files and does not advance cutoff for non-overlapping ingestion.
- Concurrent manual flush/compaction operations monotonically advance the effective cutoff.

## Dependencies and Integration Points

The file integrates with `db/db_impl/db_impl.h`, `db/db_test_util.h`, `options/options_parser.h`, `ColumnFamilyHandleImpl`, `ColumnFamilyData`, `VersionStorageInfo`, `WriteController`, `PeriodicTaskScheduler`, `FaultInjectionTestEnv`, `SpecialEnv`, `SyncPoint`, custom comparators, merge operators, table property collectors, external SST ingestion, and RocksDB public DB/iterator/listener APIs.

## Risks and Edge Cases

- Many tests rely on precise background timing. `SyncPoint` dependencies and sleeping background tasks reduce flakiness but can deadlock if production sync-point labels change.
- WAL counting uses `GetSortedWalFiles()` with retries because concurrent deletion can make the API flaky.
- Some tests use disabled cases (`DISABLED_CreateAndDropRace`, `DISABLED_LogTruncationTest`) documenting races or recovery scenarios that are currently hard to run reliably.
- Internal API use (`TEST_*`, direct `ColumnFamilyData`/`VersionStorageInfo` mutation) gives good coverage but couples the suite tightly to implementation structure.
- UDT behavior depends on timestamp comparator format and on subtle interactions among flush scheduling, write-stall avoidance, and cutoff advancement.

## Test Signals

This file is itself a test target. Strong signals include reopen/recovery checks, live file/WAL counts, compaction level layouts, explicit status class assertions, table property assertions, sync-point-controlled races, and iteration count/value checks. It provides regression coverage for manifest persistence, WAL lifecycle, dropped-CF handle semantics, compaction scheduler conflicts, write-stall thresholds, and UDT-retention garbage collection.
