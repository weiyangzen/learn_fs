# sources/storage-engines/rocksdb/db/db_dynamic_level_test.cc

## Purpose

`db_dynamic_level_test.cc` is a RocksDB GoogleTest suite for leveled compaction with `level_compaction_dynamic_level_bytes=true`. It validates how RocksDB computes and changes the base level as data volume grows, how dynamic-level layout interacts with automatic and manual compaction, and whether the DB remains readable while the base level migrates.

The file is not production code, but it acts as a behavioral specification for dynamic LSM level sizing. It checks level metadata, compaction output levels, background error counters, and key visibility after flushes, compactions, reopen, and a disabled migration scenario from static to dynamic level sizing.

## Important APIs, Types, and Helpers

- `DBTestDynamicLevel : public DBTestBase` is the test fixture. It uses the test DB name `db_dynamic_level_test` and enables fsync behavior through `env_do_fsync=true`.
- `Options` fields under test include `level_compaction_dynamic_level_bytes`, `max_bytes_for_level_base`, `max_bytes_for_level_multiplier`, `num_levels`, `target_file_size_base`, `write_buffer_size`, `max_write_buffer_number`, L0 compaction/slowdown/stop triggers, `max_background_compactions`, `max_compaction_bytes`, `compression_per_level`, `disable_auto_compactions`, `db_host_id`, and `table_factory`.
- Public and test DB APIs used include `DestroyAndReopen`, `Reopen`, `Put`, `Delete`, `Get`, `Flush`, `CompactRange`, `SetOptions`, `TEST_WaitForCompact`, `GetIntProperty`, `GetProperty`, `GetColumnFamilyMetaData`, and `NumTableFilesAtLevel`.
- Internal synchronization uses `ROCKSDB_NAMESPACE::SyncPoint`, with dependencies around `CompactionJob::Run():Start`, `CompactionJob::Run():End`, `FlushJob::WriteLevel0Table`, and test-defined sync labels.
- Metadata APIs include `ColumnFamilyMetaData` and its per-level file lists, plus properties such as `rocksdb.base-level`, `rocksdb.background-errors`, and `rocksdb.num-files-at-levelN`.
- Helper utilities include `Random`, `RandomShuffle`, `PutFixed32`, `DecodeFixed32`, compression capability checks (`Snappy_Supported`, `LZ4_Supported`), `NewBlockBasedTableFactory`, `BlockBasedTableOptions`, and `port::Thread`.

## Control Flow and State Behavior

`DynamicLevelMaxBytesBase` runs a broad stress scenario across ordered and shuffled key insertion, and across one and three background compaction threads. It configures five levels, small memtables and target files, dynamic level bytes, and per-level compression. The test writes three key bands, deletes one tenth of the middle band, and sleeps briefly between batches to let background work run. It then asserts no background errors, verifies data before and after reopen, performs a full manual compact range, and confirms all files end up in the last level while the data/deletion contract still holds.

`DynamicLevelMaxBytesBase2` targets base-level transitions with controlled data volumes. It disables auto compaction, writes roughly 28 KiB, re-enables compaction, flushes, waits, and confirms the base level starts at L4. A second roughly 28 KiB batch moves the base to L3 while L1 and L2 remain empty. Another roughly 40 KiB leaves the base at L3. A much larger roughly 650 KiB load uses a sync point so compaction starts before the last flush, preventing a jump directly to L1 and asserting the base becomes L2. The final phase runs a manual `CompactRange` in another thread while more writes and a flush occur, then verifies the base advances to L1.

`DynamicLevelMaxBytesCompactRange` verifies manual compaction behavior when the current base level is not L1. It compacts an empty DB, writes data, flushes and waits for background compaction, ensures L0 is non-empty if automatic work drained it, and expects the base level to be L3 with L1/L2 empty. A `SyncPoint` callback observes `CompactionPicker::CompactRange:Return` and records output levels. A full compact range should emit compactions to both L3 and L4, drain L0 and L3, and keep `rocksdb.base-level` at L3.

`DynamicLevelMaxBytesBaseInc` checks that increasing the base level through dynamic sizing does not schedule non-trivial background compactions unnecessarily. A sync callback counts `DBImpl::BackgroundCompaction:NonTrivial`. After inserting 3000 keys with a random prefix and a fixed suffix encoding the key index, the test flushes, waits for compaction, asserts the non-trivial count is zero, and reads every key back to verify value integrity.

`DISABLED_MigrateToDynamicLevelMaxBytesBase` documents a migration scenario from static level bytes to dynamic level bytes. It first writes and deletes keys under static sizing, reopens with dynamic sizing and auto compaction disabled, verifies data, runs a manual compact range to the last level in a background thread while repeatedly reading, re-enables auto compaction, writes more data, waits for compaction, and asserts L1/L2 are empty. Because the test is disabled, it is guidance and regression documentation rather than a normal test signal.

## State and Persistence Behavior

The suite observes LSM placement rather than durable byte-for-byte file contents. Persistent state under test includes flushed SST files, level assignment metadata, deletion tombstones, compaction outputs, base-level property state, and DB contents across close/reopen.

Dynamic level bytes make the base level depend on accumulated data size. Early data lands in the last level, then as total bytes grow the base level moves upward from L4 to L3, L2, and finally L1. The tests assert that intermediate levels below the base can remain empty and that compaction output chooses the computed base and deeper levels rather than assuming L1 is always the starting non-L0 level.

Manual full compaction is expected to preserve live keys, honor deleted keys, and eventually place data in the deepest level when compacting all ranges. Concurrent manual compaction and flush/automatic compaction must not corrupt data or leave base-level accounting stale.

Reopen checks in `DynamicLevelMaxBytesBase` verify dynamic level metadata and generated table files persist cleanly through DB close/open. The disabled migration test further documents that existing static-level DB state should remain readable when reopened with dynamic-level sizing and then compacted to the last level.

## Dependencies and Integration Points

The file integrates the DB test framework in `db/db_test_util.h` with compaction scheduling, `VersionStorageInfo` base-level computation exposed through properties, `CompactionPicker`, `CompactionJob`, `FlushJob`, block-based table sizing, compression libraries, in-memory or default environments, and background thread pools.

Important integration points are:

- RocksDB public option plumbing for dynamic level bytes and runtime `SetOptions`.
- Background compaction and manual `CompactRange` interaction, including concurrent compaction and flush.
- Property exposure for `rocksdb.base-level`, per-level file counts, and background error counts.
- Table construction and compression effects on file size estimates, especially when `db_host_id` is cleared to avoid perturbing file-size calculation in one test.
- SyncPoint labels inside compaction picker/job and flush job internals.

## Risks and Edge Cases

The tests are sensitive to file-size estimates. Small write buffers, target file sizes, block sizes, compression settings, and random value lengths are chosen to drive specific byte thresholds. Changes in table metadata overhead, compression ratio, block layout, host ID properties, or compaction expansion can shift the expected base level.

The suite relies on internal sync-point names and timing. Refactors that rename `CompactionJob`, `FlushJob`, or `CompactionPicker` sync labels can deadlock or silently reduce coverage unless the tests are updated.

Concurrency coverage is intentionally narrow but high risk. The final phase of `DynamicLevelMaxBytesBase2` verifies manual compaction and flush can overlap while base level changes to L1. Bugs here could produce stale level metadata, missed compaction, write stalls, or data loss.

Compression-gated coverage can be skipped when Snappy or LZ4 is unavailable, so release/test environments without those libraries lose part of the signal.

The disabled migration test contains useful behavior but does not protect normal CI unless explicitly enabled. Migration regressions from static to dynamic level sizing may not be caught by default.

## Test Signals

Strong signals include successful `db_dynamic_level_test` runs with `rocksdb.background-errors == 0`, expected `rocksdb.base-level` transitions from L4 to L3 to L2 to L1, empty L1/L2 properties when the base is L3, expected compaction output levels during compact range, and all point reads/deletions matching expected visibility before and after reopen.

Metadata checks such as `ColumnFamilyMetaData` level file counts and `rocksdb.num-files-at-levelN` properties provide direct evidence that dynamic-level placement is correct. SyncPoint callbacks verify specific internal paths, including non-trivial compaction avoidance and compact-range output-level selection.
