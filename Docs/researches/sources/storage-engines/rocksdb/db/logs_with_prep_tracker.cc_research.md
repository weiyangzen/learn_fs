<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/logs_with_prep_tracker.cc -->
# sources/storage-engines/rocksdb/db/logs_with_prep_tracker.cc

## Purpose
Implements tracking of WAL files that contain outstanding two-phase-commit prepare sections. The tracker lets obsolete-file discovery keep the earliest WAL that might still contain an uncommitted or unaborted prepared transaction.

## Important APIs, Types, And Functions
`MarkLogAsContainingPrepSection(log)` records one prepare section in a log, maintaining `logs_with_prep_` as a sorted vector of `{log, cnt}` entries. `MarkLogAsHavingPrepSectionFlushed(log)` records completion of one prepared section in `prepared_section_completed_`, a log-number-to-count map. `FindMinLogContainingOutstandingPrep()` reconciles both structures and returns the smallest log still containing an outstanding prepare, or zero if none remain.

## Control Flow
Prepare paths call `MarkLogAsContainingPrepSection()`, which locks `logs_with_prep_mutex_`, searches from the vector end because new prepares are usually in the latest log, increments an existing count or inserts a new sorted entry. Commit/abort/flush completion calls `MarkLogAsHavingPrepSectionFlushed()`, which only locks the completion map and increments the completed count. The min lookup locks the sorted vector, then for each smallest log locks the completion map briefly. If completions are missing or fewer than prepares, it returns that log. If counts match, it erases both structures and advances.

## State And Persistence Behavior
The state is in-memory and count-based. It does not persist transaction status itself; it protects WAL retention by reporting the earliest WAL that cannot yet be deleted. Returning zero means no known prepared sections require WAL retention. Completed counts are lazily reconciled to reduce contention on prepare insertion paths.

## Dependencies And Integration Points
Depends on `logs_with_prep_tracker.h` and `port/likely.h`. It integrates with transaction prepare/commit/abort flows and obsolete WAL cleanup logic. `MemTable::RefLogContainingPrepSection()` is a related per-memtable signal for the minimum referenced prepare log.

## Risks And Edge Cases
Both mark APIs assert nonzero log numbers. The vector erase-from-front in `FindMinLogContainingOutstandingPrep()` is intentionally not optimized because it is not on the fast path. Correctness depends on matching each prepare mark with exactly one completion mark; mismatched counts can retain WALs indefinitely or permit deletion too early. Lock ordering is vector mutex then completion mutex in the min lookup; other methods lock only one mutex, reducing deadlock risk.

## Test Signals
The header exposes `TEST_PreparedSectionCompletedSize()` and `TEST_LogsWithPrepSize()` for unit tests. Behavior is typically verified through transaction/WAL-retention tests that check obsolete log deletion around prepared transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/logs_with_prep_tracker.cc -->
