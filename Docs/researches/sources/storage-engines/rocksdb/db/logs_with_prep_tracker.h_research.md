<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/logs_with_prep_tracker.h -->
# sources/storage-engines/rocksdb/db/logs_with_prep_tracker.h

## Purpose
Declares `LogsWithPrepTracker`, a small concurrency-aware helper for tracking WAL files with outstanding prepared transaction sections.

## Important APIs, Types, And Functions
Public methods are `MarkLogAsHavingPrepSectionFlushed()`, `MarkLogAsContainingPrepSection()`, `FindMinLogContainingOutstandingPrep()`, and two test-size accessors. The private `LogCnt` struct stores a log number and prepare-section count. The class uses `logs_with_prep_` plus `logs_with_prep_mutex_` for sorted prepare counts and `prepared_section_completed_` plus `prepared_section_completed_mutex_` for completed counts.

## Control Flow
The header establishes a two-lane update design: prepare writers update the sorted vector, while commit/abort completion writers update a separate map. The min lookup reconciles the two. This avoids making every completion contend with prepare insertion in the common path.

## State And Persistence Behavior
All state is in-memory. Its output influences persistence indirectly by determining the oldest WAL that must be retained for transaction recovery. The zero return value from `FindMinLogContainingOutstandingPrep()` means no log is currently protected by this tracker.

## Dependencies And Integration Points
Uses standard mutex, unordered map, vector, assertions, and RocksDB namespace configuration. It is part of DB transaction/WAL lifecycle code and should be considered when changing WAL cleanup or prepared-transaction recovery.

## Risks And Edge Cases
The sorted-vector invariant and count matching are essential. The two mutexes protect different structures, so any future code touching both must preserve the lock order used by the implementation. The test accessors are not locked and should be used only in controlled test contexts.

## Test Signals
Direct tests can inspect container sizes after mark/reconcile operations. Higher-level tests should verify WAL retention under multiple prepares in the same log, prepares spanning logs, and out-of-order completions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/logs_with_prep_tracker.h -->
