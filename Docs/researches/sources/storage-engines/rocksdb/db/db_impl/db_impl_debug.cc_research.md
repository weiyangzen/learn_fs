<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_debug.cc -->
# sources/storage-engines/rocksdb/db/db_impl/db_impl_debug.cc

## Purpose

`db_impl_debug.cc` provides non-release `DBImpl::TEST_*` hooks compiled only when `NDEBUG` is not defined. It gives unit and stress tests controlled access to internal DB state and operations that are otherwise hidden behind production APIs: memtable/WAL switching, flush/compaction forcing, background wait loops, file metadata inspection, cache verification, periodic scheduler hooks, write-thread entry, and background error state.

The file is intentionally not part of production builds. Its role is to make internal invariants observable and to let tests create specific DB states without duplicating DB internals.

## Important APIs, Types, and Functions

- State readers: `TEST_GetLevel0TotalSize()`, `TEST_MaxNextLevelOverlappingBytes()`, `TEST_Current_Manifest_FileNo()`, `TEST_Current_Next_FileNo()`, `TEST_LogfileNumber()`, `TEST_GetBGError()`, `TEST_IsRecoveryInProgress()`, `TEST_BGCompactionsAllowed()`, `TEST_BGFlushesAllowed()`, `TEST_NumRunningBottomCompactions()`, `TEST_GetLastVisibleSequence()`, `TEST_GetSeqnoToTimeMapping()`, and `TEST_GetFilesToQuarantine()`.
- Metadata extraction: `TEST_GetFilesMetaData()` copies per-level `FileMetaData` and optionally blob metadata from the current version storage.
- Forced state transitions: `TEST_SwitchWAL()`, `TEST_SwitchMemtable()`, `TEST_FlushMemTable()`, `TEST_AtomicFlushMemTables()`, and `TEST_CompactRange()` invoke internal write/flush/compaction machinery with test reasons and controlled options.
- Wait helpers: `TEST_WaitForBackgroundWork()`, `TEST_WaitForFlushMemTable()`, `TEST_WaitForCompact()`, `TEST_WaitForPurge()`, and `TEST_WaitForPeriodicTaskRun()` expose blocking synchronization points.
- Lock/write helpers: `TEST_LockMutex()`, `TEST_UnlockMutex()`, `TEST_SignalAllBgCv()`, `TEST_BeginWrite()`, and `TEST_EndWrite()` allow tests to stage specific interleavings.
- Cache and file-lifetime helpers: `TEST_GetAllBlockCaches()`, `TEST_DeleteObsoleteFiles()`, and `TEST_VerifyNoObsoleteFilesCached()` validate cache/file cleanup invariants.
- Transaction/WAL-prep helpers: `TEST_FindMinLogContainingOutstandingPrep()`, `TEST_PreparedSectionCompletedSize()`, `TEST_LogsWithPrepSize()`, and `TEST_FindMinPrepLogReferencedByMemTable()` expose prepared-section tracking internals.
- Option/scheduler helpers: `TEST_GetLatestMutableCFOptions()`, `TEST_GetWalPreallocateBlockSize()`, and `TEST_GetPeriodicTaskScheduler()`.

## Control Flow

Most functions are thin wrappers that acquire `mutex_` or another internal mutex, read or call the underlying `DBImpl` method, and return the result. Column-family arguments are normalized by using the default CF when the caller passes null or by casting `ColumnFamilyHandleImpl` to access `ColumnFamilyData`.

`TEST_SwitchWAL()` and `TEST_SwitchMemtable()` enter the unbatched write-thread path before invoking internal switch routines so tests preserve the same write-thread invariants as production transitions. When `two_write_queues_` is enabled, `TEST_SwitchMemtable()` also enters/exits `nonmem_write_thread_`.

`TEST_FlushMemTable()` constructs `FlushOptions` or accepts supplied options and calls `FlushMemTable()` with `FlushReason::kTest`. `TEST_AtomicFlushMemTables()` similarly calls `AtomicFlushMemTables()` with test reason. `TEST_CompactRange()` calculates the expected output level for leveled versus universal/FIFO compaction and delegates to `RunManualCompaction()`.

`TEST_VerifyNoObsoleteFilesCached()` is the most substantial helper. In ASAN-like builds where heap allocation cleanup is required, it optionally locks the DB mutex, builds a set of live/quarantined SST and blob file numbers from all live versions, active/protected blob partition manager state, and `ErrorHandler` quarantine state, then applies a callback to all table-cache entries asserting every cached file is still live or quarantined.

## State and Persistence Behavior

This file does not introduce independent persistent state. Instead, it invokes production paths that may persist state: WAL switching can create/sync WAL metadata through normal internals, memtable switching changes mutable/immutable lists, flush and compaction wrappers create SSTs and MANIFEST edits, and obsolete-file deletion can remove files.

Read helpers expose in-memory and persisted metadata snapshots while holding the appropriate mutex. `TEST_GetFilesMetaData()` copies current version file metadata by value, and blob metadata by shared pointer, so tests can inspect LSM layout without owning internal `VersionStorageInfo`.

The cache verification helper treats live versions, direct-write blob manager active/protected files, and quarantined files as allowed cache residents. Any table-cache entry outside that set is considered an obsolete open-file leak and triggers assertion diagnostics.

## Dependencies and Integration Points

`db_impl_debug.cc` depends on core DB internals (`ColumnFamilyData`, `VersionStorageInfo`, `ErrorHandler`, write threads, WAL/prepared trackers), blob subsystems (`BlobFileCache`, `BlobFilePartitionManager`), block-based table options for cache discovery, `PeriodicTaskScheduler`, and thread-status/cast utilities.

Its main integration point is the RocksDB test suite. It provides direct hooks for tests that need deterministic control over compaction/flush scheduling, background waits, file cleanup, WAL numbering, block cache membership, mutable CF options, and scheduler execution.

## Risks and Edge Cases

- These functions are compiled only in debug builds. Tests depending on them cannot run against release binaries without alternate hooks.
- Several helpers expose raw internal synchronization primitives. Misusing `TEST_LockMutex()`/`TEST_UnlockMutex()` or write-thread entry helpers can deadlock tests or violate production lock ordering.
- Forced flush/compaction helpers execute real production side effects, so tests must clean up DB files and background work just as with public APIs.
- `TEST_VerifyNoObsoleteFilesCached()` is intentionally restricted to heap-cleanup/ASAN-style builds because it scans caches and can be expensive or noisy in broad test configurations.
- Some readers return values without taking the DB mutex, such as current next file number through `VersionSet`; tests should treat these as diagnostic helpers rather than general concurrency-safe APIs unless the underlying method provides safety.

## Test Signals

Every symbol in this file is itself a test signal. The breadth of exposed helpers indicates that RocksDB tests assert internal L0 sizing, manifest/file-number allocation, exact file metadata, manual compaction behavior, atomic flush behavior, background error recovery, purge completion, block-cache ownership, prepared transaction WAL retention, periodic task execution, stats-history memory accounting, and obsolete-file cache cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_debug.cc -->
