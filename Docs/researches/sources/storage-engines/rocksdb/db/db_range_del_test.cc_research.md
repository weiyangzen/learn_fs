# sources/storage-engines/rocksdb/db/db_range_del_test.cc

## Purpose
`db_range_del_test.cc` is RocksDB's extensive regression suite for range deletion tombstones. It specifies `DB::DeleteRange()` semantics, unsupported configurations, flush and compaction behavior, snapshot visibility, merge-operand interactions, iterator reseek and sentinel-key behavior, file-boundary handling, compensated range-deletion size accounting, and error propagation.

The file is especially important because range tombstones are represented across multiple layers: memtables, immutable memtables, SST range-deletion blocks, `RangeDelAggregator`, `MergingIterator`, level iterators, compaction outputs, file metadata, table properties, and read options such as snapshots, upper bounds, and `ignore_range_deletions`.

## Important APIs, Types, And Functions
The primary fixture is `DBRangeDelTest : public DBTestBase`, using database name `db_range_del_test` and `env_do_fsync=false`. It adds `GetNumericStr(int)`, which encodes integers as eight-byte `uint64_t` keys for tests using `test::Uint64Comparator()`.

The main public API under test is `db_->DeleteRange(WriteOptions(), ColumnFamilyHandle*, begin, end)`, plus `WriteBatch::DeleteRange()` and unsupported `WriteBatchWithIndex::DeleteRange()`. The tests heavily use `Put`, `Merge`, `Delete`, `Flush`, `CompactRange`, `CompactFiles`, `MoveFilesToLevel`, `NumTableFilesAtLevel`, `FilesPerLevel`, `Get`, `NewIterator`, `GetSnapshot`/`ReleaseSnapshot`, `SetOptions`, and `GetPropertiesOfAllTables()`.

Internal/test integration APIs include `dbfull()->TEST_CompactRange()`, `RunManualCompaction()`, `TEST_GetFilesMetaData()`, `TEST_GetLevelIterator()`, `TEST_WaitForFlushMemTable()`, `TEST_WaitForCompact()`, `TablesRangeTombstoneSummary()`, `TableCache::Evict()`, `ColumnFamilyHandleImpl::cfd()`, `SuperVersion`, `MergeIteratorBuilder`, `InternalIterator`, `InternalKey`, `IterKey`, `RangeDelAggregator` behavior observed through iterator results, and perf-context counter `internal_range_del_reseek_count`.

Local helper and mock types cover specific risks. `MockMergeOperator` is intentionally non-associative. `SingleKeySstPartitioner` and `SingleKeySstPartitionerFactory` force partitions after every key. `TombstoneTestSstPartitioner` and its factory force a partition around `Key(5)`. `VerifyIteratorReachesEnd()` and `VerifyIteratorKey()` compactly assert iterator state and key sequences.

## Control Flow
The first tests establish API boundaries. Non-block-based table configurations and row cache reject range deletion, and `WriteBatchWithIndex` returns not-supported. Empty `[start, start)` ranges cover nothing, while `end < start` returns invalid argument and leaves data intact. Flush and compaction can emit files containing only range tombstones, including dictionary-compressed output, as long as snapshots protect tombstones from becoming obsolete.

Flush and compaction removal tests create puts around a tombstone and verify covered keys disappear while keys outside the half-open range, newer keys, and snapshot-visible keys remain. `FlushRangeDelsSameStartKey` and `CompactRangeDelsSameStartKey` exercise overlapping tombstones with the same lower bound. `CompactionRemovesCoveredKeys` and `CompactionRemovesCoveredMergeOperands` use ticker counts and `ignore_range_deletions` reads to prove compaction physically drops covered point keys or merge operands. `PutDeleteRangeMergeFlush` protects a sequence where a covered put must not reappear after merge processing.

File-boundary tests construct LSM layouts with fixed memtable factories, target file sizes, `max_compaction_bytes`, and manual level moves. They validate that tombstones spanning multiple output files do not create overlapping file ranges, that sentinel tombstones are omitted from physical outputs, that range tombstone end keys can be SST largest keys without corrupting overlap invariants, and that tombstones are written only to the minimal necessary SSTs. Related tests cover subcompactions, universal compaction, TTL-driven file cuts, SST partitioner cuts, oversized compaction gaps, overlapped tombstones, overlapped point keys, and non-bottommost compaction dropping only tombstones that do not overlap lower-level files and are not snapshot-protected.

Read-path tests verify coverage from every storage tier. `GetCoveredKeyFromMutableMemtable`, `GetCoveredKeyFromImmutableMemtable`, and `GetCoveredKeyFromSst` check point reads. `GetCoveredMergeOperandFromMemtable`, `KeyAtOverlappingEndpointReappears`, `UntruncatedTombstoneDoesNotDeleteNewerKey`, and `DeletedMergeOperandReappearsIterPrev` stress merge operands, overlapping endpoints, sequence-number zeroing, and forward/backward traversal modes. `GetIgnoresRangeDeletions` and `IteratorIgnoresRangeDeletions` ensure `ReadOptions::ignore_range_deletions` sees underlying keys in SST, immutable memtable, and mutable memtable.

Iterator tests cover normal snapshots, refresh, tailing unsupported status, reseek counters, sentinels, prefix seeks, upper bounds, file-read errors, and released snapshots. They build multi-level layouts with tombstones in memtable/L0/L1/L2/L3 and assert exact forward/backward key sequences for `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, `Next`, `Prev`, and `Refresh(snapshot)`. Low-level tests use `LevelIterator` directly and expect sentinel keys at tombstone boundaries so covered lower-level keys are skipped even when a file has only tombstones or the seek target is outside point-key bounds.

Compensated-size tests verify `FileMetaData::compensated_range_deletion_size` during flush, compaction, and reopen. They compute lower-level file sizes with `Size()`, add tombstones covering those files, and assert the compensated size equals overlapped lower-level file sizes, is persisted through reopen, and is not double-counted when identical lower/upper bounds appear at different sequence numbers.

The final tests address edge cases. `SingleKeyFile`, `AddRangeDelsSameLowerAndUpperBound`, and `AddRangeDelsSingleUserKeyTombstoneOnlyFile` force compaction output cuts around multiple versions of one user key and around tombstone-only output so file smallest/largest keys remain valid. `MemtableMaxRangeDeletions` checks the dynamic option that causes flush when too many range tombstones accumulate. `RangeDelReseekAfterFileReadError` injects retryable IO errors and proves range-del reseek does not clear iterator error status. `ReleaseSnapshotAfterIteratorCreation` ensures iterators do not dereference `ReadOptions::snapshot` after construction, and `SeekForPrevTest` verifies user-visible reverse seeks after deleting the middle of a partitioned SST layout.

## State And Persistence Behavior
The suite treats range tombstones as durable, sequence-numbered records with half-open user-key bounds. Tombstones may live in mutable memtables, immutable memtables, L0, or deeper levels; flush and compaction decide whether to preserve, truncate, split, or drop them according to snapshots, bottommost status, lower-level overlap, and output file boundaries.

Snapshots are central state. Many tests hold snapshots to prevent tombstones or covered keys from being dropped during flush/compaction, then release them to permit sequence-number zeroing or obsolete-tombstone cleanup. Snapshot reads and iterator refresh with snapshot must see keys that were visible before a tombstone, even if newer live reads skip them.

Persistent file metadata is heavily asserted. Tests inspect `FileMetaData::smallest`, `largest`, `smallest_seqno`, table properties `num_range_deletions`, live file metadata, level file counts, and compensated range-deletion size. Reopen tests prove compensated sizes survive MANIFEST recovery. Meta-level invariants include non-overlapping files at a level, tombstone end keys used as upper bounds without overlap, and valid smallest/largest ordering even for tombstone-only or single-user-key output.

Read options can change visibility without rewriting state. `ignore_range_deletions` exposes covered keys/merge operands for verification; `iterate_upper_bound` must keep tombstones outside the bound from entering merging-iterator heaps; `read_tier=kMemtableTier` with iterator refresh must not double-free stale memtable tombstone iterators; tailing iterators reject range tombstones.

## Dependencies And Integration Points
This file depends on `db/db_test_util.h`, `db/version_set.h`, `rocksdb/utilities/write_batch_with_index.h`, test utility assertions, random generation, and merge operators. It also reaches into RocksDB internals through column-family handles, version/super-version level iterators, table cache eviction, internal key construction, manual compaction helpers, sync points, perf context, and file metadata inspection.

Integration points include block-based table-only range deletion support, row cache incompatibility, memtable factories and bloom filters, prefix extractors and Bloom filters, compaction picker/output splitting, `RangeDelAggregator`, `MergingIterator`, `LevelIterator` sentinel generation, `CompactionIterator`, merge operator semantics, snapshot stripe ordering, table property accounting, `SstPartitioner`, FIFO/TTL compaction, universal and leveled compaction, background flush/compaction scheduling, and filesystem read-error propagation.

## Risks
Range deletion correctness is high risk because the same tombstone must affect reads, iterators, compaction, metadata, and file boundaries consistently. Off-by-one errors on half-open bounds can delete the endpoint, fail to delete the start, or place tombstones in files whose key range does not actually overlap the tombstone.

Iterator direction changes are subtle. Several regressions involve using the wrong range-del positioning mode while scanning merge operands, sentinel keys remaining at heap tops, or reseek logic skipping too far. Tests check both user iterators and internal level iterators to catch these issues.

Compaction output splitting is another risk. Range tombstones can force or inhibit file cuts, add compensated size, span files, or create tombstone-only outputs. Incorrect handling can violate non-overlap invariants, double-count lower-level overlap, retain obsolete tombstones, or drop snapshot-protected tombstones.

The test suite is sensitive to internal names and layout heuristics. SyncPoint callbacks, exact file counts, manual compaction targets, target file sizes, and partitioner decisions are chosen to force specific internal paths; legitimate compaction behavior changes may require updating the tests while preserving the same invariants.

## Test Signals
Strong success signals include not-supported/invalid-argument status for unsupported APIs, exact not-found/found behavior for covered and uncovered keys, correct merge sums with and without `ignore_range_deletions`, expected ticker increments for keys/tombstones dropped by compaction, non-overlapping file metadata after compaction, and exact table-property range-deletion counts.

Iterator signals are especially valuable: expected forward and backward key sequences across snapshots and levels, `internal_range_del_reseek_count` increments only where tombstones force reseeks, tailing iterator not-supported status, refresh respecting snapshots across mutable/immutable/L0/L1 states, upper-bound tests avoiding tombstone heap processing, and injected IO errors remaining visible after range-del reseek.

Metadata and persistence signals include correct `compensated_range_deletion_size` during flush/compaction/reopen, no double-counting identical tombstone bounds, stable smallest/largest internal keys around tombstone sentinels, valid behavior for tombstone-only files/levels, dynamic `memtable_max_range_deletions` triggering flush, and row cache rejecting range deletion without leaving the DB read-only.
