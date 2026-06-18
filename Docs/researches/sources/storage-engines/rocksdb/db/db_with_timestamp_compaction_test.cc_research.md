# sources/storage-engines/rocksdb/db/db_with_timestamp_compaction_test.cc

## Purpose
`db_with_timestamp_compaction_test.cc` is a targeted RocksDB integration test suite for compaction behavior when a column family uses user-defined timestamps. It verifies that compaction picks complete timestamp-compatible input ranges, preserves timestamp visibility across file boundaries and subcompactions, handles `CompactFiles()` range expansion, applies `full_history_ts_low` correctly to sequence-number zeroing and bottommost compaction scheduling, and persists file timestamp ranges through flush, compaction, external SST ingestion, manifest reopen, and table properties.

Compared with the broader basic timestamp suite, this file focuses on compaction metadata and file-level correctness. It inspects `FileMetaData::min_timestamp` and `max_timestamp`, compaction input lists, output file counts, and sync-point events in addition to read results.

## Important APIs, Types, And Functions
The local helpers `Key1(uint64_t)` and `Timestamp(uint64_t)` encode ordered test keys and 8-byte timestamps. `TimestampCompatibleCompactionTest` derives from `DBTestBase` and provides:

- `Get(key, ts)`, a timestamped read wrapper returning `"NOT_FOUND"` or status text for assertions.
- `GetAllFileTimestamps()`, which reaches through `ColumnFamilyHandleImpl` and current `VersionStorageInfo` to collect every live file's level, min timestamp, and max timestamp.
- `GetOverallTimestampRange()`, which decodes file timestamp ranges and computes the DB-wide min/max.
- `VerifyTimestampRangeWithPersistence()`, which checks min/max before and after `Reopen()`.
- `CreateTimestampOptions()`, which enables level compaction, `persist_user_defined_timestamps`, and `BytewiseComparatorWithU64TsWrapper`.
- `WriteDataWithTimestampRange()`, `HasFileWithTimestampRange()`, and `VerifyDataReadable()` helpers.

`TestFilePartitioner` and `TestFilePartitionerFactory` force compaction output partitioning and disallow trivial moves so tests can observe range expansion and output file construction. The file also uses `CompactionJobInfo`, `CompactFiles`, `CompactRange`, `RunManualCompaction`, `SstFileWriter`, `SstFileReader`, external file ingestion, table properties, `IncreaseFullHistoryTsLow`, snapshots, and sync points such as `CompactionIterator::PrepareOutput:ZeroingSeq`.

## Control Flow
`UserKeyCrossFileBoundary` creates three L0 files with overlapping user key `99` at increasing timestamps. A sync point verifies level compaction picks all three L0 files as one timestamp-compatible input group. After compaction, reads at saved timestamps must return the historical values `foo_99`, `bar_99`, and `foo1_99`, proving compaction did not split versions of the same user key across incompatible file boundaries.

`MultipleSubCompactions` writes 1000 timestamped keys under universal compaction with `max_subcompactions=3`, small target files, and statistics. It runs a manual compaction and asserts the `NUM_SUBCOMPACTIONS_SCHEDULED` histogram sum is greater than one, then reads every key at a high timestamp to validate subcompaction boundary handling with timestamped keys.

`CompactFilesRangeCheckL0` and `CompactFilesRangeCheckL1` exercise `DB::CompactFiles()` input expansion. The L0 test supplies one middle L0 file for a repeated user key and expects older overlapping L0 files to be included. The L1 test first compacts repeated timestamp versions to L1 using a forced partitioner, then adds L0 files and supplies a mixed input set; it expects all relevant L1 and L0 files to be included and each partitioned output to be accounted for.

`EmptyCompactionOutput` writes only a timestamped range tombstone, compacts with `full_history_ts_low` beyond the tombstone timestamp and forced bottommost compaction, and expects success even when the compaction drops everything and produces no output.

`SeqnoZeroingWithUDT` installs a sync-point callback when compaction zeroes sequence numbers. It proves no zeroing happens when UDT is enabled but `full_history_ts_low` is unset, that keys below the low watermark are zeroed, and that a key with timestamp at or above the low watermark is not zeroed. It then confirms all values remain readable at a later timestamp.

The bottommost compaction tests ensure files are not repeatedly marked for bottommost compaction when their max timestamp is still at or above `full_history_ts_low`, or when `full_history_ts_low` has never been set. Once the low watermark moves beyond the file's max timestamp, snapshot release and compaction can proceed normally.

The final metadata tests validate timestamp-range persistence. One creates an external SST with UDT table properties, ingests it, checks `FileMetaData` min/max timestamps, reopens, and reads data. The flush test checks table properties and file metadata after one flush. The compaction test writes three L0 files with disjoint timestamp ranges, compacts them, and verifies the merged file range is the min of all inputs and max of all inputs before and after reopen.

## State And Persistence Behavior
This suite centers on persistent file metadata. Timestamp ranges collected during table building must become table properties, then `FileMetaData::min_timestamp` and `max_timestamp`, then manifest records that survive reopen. Compaction must merge input timestamp ranges into output metadata, and external SST ingestion must extract timestamp table properties into file metadata even though the file was built outside the DB.

Compaction state is also validated through input selection. When multiple files contain different timestamp versions of the same user key, compaction must include the complete overlapping set needed for correct visibility. `CompactFiles()` cannot blindly compact only the user-supplied file when timestamp-compatible older/newer inputs are necessary.

`full_history_ts_low` controls whether history is old enough for sequence-number zeroing or bottommost cleanup. The tests require the low watermark to be set and greater than a file/key timestamp before zeroing or marking is allowed. Otherwise data remains readable and files should not enter an infinite bottommost compaction loop.

## Dependencies And Integration Points
The file depends on `db/db_test_util.h`, `db/column_family.h`, `db/compaction/compaction.h`, `rocksdb/sst_file_reader.h`, `test_util/testutil.h`, and `port/stack_trace.h`. It integrates with public DB APIs, internal column-family and version-storage types, compaction picker behavior, compaction iterators, subcompaction statistics, file partitioners, external SST writer/reader/ingestion, table-property collectors, manifest reopen, and snapshot-triggered bottommost file marking.

The comparator used in most tests is `test::BytewiseComparatorWithU64TsWrapper()`, making these tests a direct exercise of RocksDB's built-in U64 timestamp mode rather than the custom 16-byte comparator used in parts of the basic suite.

## Risks
Compaction range selection is the main correctness risk. If files are split or omitted around the same user key with different timestamps, old reads can return the wrong version after compaction even when latest reads look correct. The tests for repeated key `99` and `CompactFiles()` input expansion are targeted at that hazard.

Metadata extraction is another risk. Missing min/max timestamps in `FileMetaData` can disable timestamp table filtering, break bottommost marking decisions, or lose newest/oldest timestamp information after reopen. External SST ingestion is especially sensitive because the file metadata is created outside normal flush/compaction paths.

`full_history_ts_low` must avoid two opposite failures: zeroing sequence numbers too early, which can expose data incorrectly across snapshots, and failing to zero/mark old files when safe, which can retain history or trigger repeated compactions. Tests use sync points and timeouts to detect both types.

## Test Signals
Success signals include correct historical values after cross-file compaction, more than one scheduled subcompaction, expanded `CompactionJobInfo::input_files` counts, expected partitioned output counts, successful empty compaction output, exact sync-point zeroed-key sets, no timeout in bottommost compaction waiting, table properties containing `rocksdb.timestamp_min` and `rocksdb.timestamp_max`, file metadata min/max ranges matching expected decoded values, and the same metadata after reopen.

Failures typically indicate incomplete compaction input expansion, invalid timestamp-aware subcompaction boundaries, incorrect sequence-number zeroing with UDT, bottommost compaction loops, missing timestamp table properties, or manifest persistence gaps for timestamp ranges.
