<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_job_stats_test.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_job_stats_test.cc

## Purpose

`compaction_job_stats_test.cc` is a parameterized RocksDB unit test for listener-visible `CompactionJobStats`. It builds controlled LSM layouts, triggers manual and automatic compactions, and verifies that `CompactionJobInfo::stats` reports expected input/output record counts, file counts, byte estimates, raw key/value bytes, replacement/deletion counters, key prefixes, full/manual flags, and optional IO timing fields.

The suite runs with `max_subcompactions` values `1` and `4`, so it checks both sequential compaction and subcompaction-sensitive behavior.

## Important APIs, Types, and Functions

- `RandomString()` and `Key()` generate compressible values and fixed-width numeric keys.
- `CompactionJobStatsTest` is the fixture. It owns the DB path, WAL path, `Env`, `DB`, column family handles, last options, and selected `max_subcompactions_`.
- Fixture helpers wrap DB lifecycle and operations: `Reopen()`, `DestroyAndReopen()`, `CreateAndReopenWithCF()`, `Flush()`, `Put()`, `Delete()`, `Get()`, `FilesPerLevel()`, `NumTableFilesAtLevel()`, `Compact()`, `TEST_Compact()`, `MakeTables()`, `MakeTableWithKeyValues()`, and `SelectivelyDeleteKeys()`.
- `CompactionJobStatsChecker` is an `EventListener` that queues expected `CompactionJobStats` and verifies the next `OnCompactionCompleted()` callback under a mutex.
- `CompactionJobDeletionStatsChecker` specializes verification to deletion/replacement counters.
- `EstimatedFileSize()` approximates SST sizes with data, footer, filter, and index overhead so byte counters can be checked with tolerance instead of exact equality.
- `NewManualCompactionJobStats()` builds expected stats for a compaction range, including file/record counts, estimated bytes, raw key/value bytes, flags, replacement count, and output key prefixes.
- `GetAnyCompression()` selects an available compression type for compression-tolerant stat checks.
- `GetUniversalCompactionInputUnits()` predicts which flushed runs universal compaction will compact.

## Control Flow

`CompactionJobStatsTest` fixture setup creates a fresh DB with one LOW and one HIGH background thread and parameterized `max_subcompactions`. Teardown disables sync points, closes handles, and destroys all DB paths.

`TEST_P(CompactionJobStatsTest, CompactionJobStatsTest)` performs a multi-phase level-compaction scenario on a `pikachu` column family:

1. Create eight L0 files with disjoint key ranges while auto-compaction is held off.
2. Manually compact six single L0 ranges to L1, expecting one input file, one output file, and unchanged record counts for each.
3. Compact remaining L0 files into one L1 output, expecting multiple input files but one output.
4. Generate sparse wider L0 files and compact overlapping L0/L1 ranges, expecting three input files, two files at output level, replacement of one third of records, and subcompaction-dependent output file count (`2` when `max_subcompactions > 1`, otherwise `1`).
5. Perform a broader compaction and then, when compression is available, rerun with compressed output and sync-point-induced delays to assert IO timing stats are nonzero.

`TEST_P(..., DeletionStatsTest)` builds overlapping data across L2, L1, and L0, inserts deletion records for existing and non-existing keys, then compacts L0 to L1 and verifies `num_input_deletion_records`, `num_expired_deletion_records`, and `num_records_replaced`.

`TEST_P(..., UniversalCompactionTest)` configures universal compaction, precomputes expected stats for automatic compactions after flushes, writes six flushed runs, waits for compactions, and verifies full/manual flags and input-unit accounting.

## State and Persistence Behavior

The tests create real RocksDB databases under `test::PerThreadDBPath()`, create and drop column family handles, flush memtables into SSTs, invoke manual compaction APIs, and wait for background compaction. Expected stats are queued before each compaction so the listener callback can consume them in order. The queue is protected by a mutex because compaction completion callbacks can occur on background threads.

`FilesPerLevel()` and `NumTableFilesAtLevel()` read RocksDB properties to assert that the physical LSM shape matches the expected test phase before checking stats. The tests use `DestroyAndReopen()` to reset persistent DB state between compression/no-compression runs while preserving the same listener object in options.

Sync points around `WritableFileWriter` deliberately sleep in append/flush/sync/range-sync paths so `file_write_nanos`, `file_prepare_write_nanos`, `file_fsync_nanos`, and `file_range_sync_nanos` become observable when `options.report_bg_io_stats` is true.

## Dependencies and Integration Points

The test depends on RocksDB DB APIs (`DB::Open`, column families, `CompactRange`, `Flush`, `Put`, `Delete`, properties), `DBImpl::TEST_CompactRange()` and `TEST_WaitForCompact()`, `EventListener::OnCompactionCompleted()`, sync-point instrumentation, table factories/properties, compression support helpers, and test harness utilities.

It directly validates behavior implemented in `compaction_job.cc`: stat aggregation from inputs/outputs, output key prefix copying, replacement/drop counters from `RecordDroppedKeys()`, manual/full flags from `ReportStartedCompaction()` and compaction style, subcompaction output count effects, and IO timing population from `RecordCompactionIOStats()`/finalization.

## Risks and Edge Cases

- Byte-size checks are approximate by design. They tolerate 10% normally and 20% with compression, so regressions within that tolerance may not fail.
- The tests use fixed assumptions about key/value sizes, table overhead, L0/L1 file layout, and universal compaction input grouping. Changes in table format defaults or compaction picking can require expected-stat updates.
- With `max_subcompactions > 1`, output file count differs because subcompactions do not coordinate to minimize output files like the sequential path; the test encodes this distinction.
- `CompactionJobStatsChecker` verifies only when expected stats are queued. Unexpected extra compactions can be missed except where the test asserts queue length at the end or between phases.
- IO timing assertions rely on sync-point sleeps and may be sensitive to platform-specific IO/stat behavior, which is why the entire file is disabled for `IOS_CROSS_COMPILE`.

## Test Signals

This file is itself the primary test signal for compaction job stats. It covers:

- Manual level compaction stats, including input/output levels and key prefixes.
- Replacement/drop accounting when newer records replace older records.
- Deletion-specific stats for expired deletion records and replaced records.
- Universal compaction stats and full-compaction flag behavior.
- Parameterized single-subcompaction and multi-subcompaction paths.
- Compression-aware byte estimate tolerance.
- Background IO timing fields when `report_bg_io_stats` is enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_job_stats_test.cc -->
