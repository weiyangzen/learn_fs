# sources/storage-engines/rocksdb/db/db_readonly_with_timestamp_test.cc

## Purpose

This file validates user-defined timestamp behavior after reopening a DB in read-only mode, including compacted-read-only openings. It focuses on timestamp contract enforcement for `Get`, `MultiGet`, `NewIterator`, and `NewIterators`, and on correct historical visibility when timestamped keys are stored only in SST files.

## Important APIs, Types, And Functions

- `DBReadOnlyTestWithTimestamp` derives from `DBBasicTestWithTimestampBase`, giving access to timestamp helpers such as `Timestamp`, `Key1`, `TestComparator`, and `CheckIterUserEntry`.
- `CheckDBOpenedAsCompactedDBWithOneLevel0File()` inspects `VersionSet`, `ColumnFamilyData`, `Version`, and `VersionStorageInfo` to verify compacted-read-only layout with one L0 file.
- `CheckDBOpenedAsCompactedDBWithOnlyHighestNonEmptyLevelFiles()` verifies that only the highest non-empty level has files when read-only compacted DB opens over fully compacted data.
- Tests use `ReadOnlyReopen(options)`, `options.max_open_files = -1`, `test::NewSpecialSkipListFactory`, `BytewiseComparatorWithU64TsWrapper`, and `IncreaseFullHistoryTsLow`.
- Public read APIs under test are `Get` with and without timestamp output, `NewIterator`, `NewIterators`, and vector-returning `MultiGet` overloads with optional timestamp vectors.

## Control Flow

The first group creates timestamped or non-timestamped data, closes the primary, reopens read-only, and checks invalid combinations: read timestamp size mismatch, read timestamp specified when the DB was written without timestamp support, and timestamped data read without a read timestamp. The positive `IteratorAndGet` and `Iterators` tests write two timestamp versions over overlapping key ranges, then read at two higher timestamps and verify forward scans, reverse scans, lower/upper iterator bounds, returned values, and returned write timestamps.

`FullHistoryTsLowSanityCheckFail` uses a U64 timestamp comparator with `persist_user_defined_timestamps = false`, raises `full_history_ts_low`, flushes, reopens read-only, and confirms reads below the low watermark return `InvalidArgument` through `Get`, `NewIterator`, and `NewIterators`.

The compacted DB tests flush data to SST, then reopen read-only with `max_open_files = -1`. Some cases keep a single L0 file; others run `CompactRange` so only the highest non-empty level holds files. They repeat the same invalid timestamp contract tests and positive visibility tests for `Get` and `MultiGet`.

## State And Persistence Behavior

All data is persisted before read-only reopening, so the tests cover table-file timestamp metadata rather than mutable memtable behavior. `disable_auto_compactions` is used to control L0 file shape; explicit `CompactRange` moves data into the highest non-empty level. The compacted-read-only path pins/open table readers differently because `max_open_files = -1`, and the helper assertions ensure the intended version layout is actually active.

## Dependencies And Integration Points

The file depends on timestamp-aware comparators and helper utilities in `db_with_timestamp_test_util.h`, special skip-list memtables to create predictable flush boundaries, version storage internals for layout checks, and read-only DB open paths. It integrates with timestamp encoding, full-history low watermark validation, table properties that preserve timestamp state, and compacted DB read code.

## Risks And Edge Cases

Many tests depend on fixed timestamp byte widths. A comparator timestamp-size change must update both write and read timestamp construction. Compact read-only tests require exact level/file shapes; compaction heuristics or file-size defaults can change those shapes. The loops over 0..1024 keys make the assertions robust but somewhat expensive. Invalid timestamp cases intentionally expect API-level `InvalidArgument`, so changes that silently ignore timestamps would be caught.

## Test Signals

Signals include `InvalidArgument` statuses for mismatched or missing timestamp contracts, iterator validity/status checks, exact key/value/write-timestamp comparisons through `CheckIterUserEntry`, `MultiGet` status and output vector sizes, and version-layout assertions on L0 and highest non-empty levels.
