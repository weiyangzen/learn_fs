# sources/storage-engines/rocksdb/db/db_iterator_test.cc

## Purpose

This file is a large RocksDB gtest suite for DB iterator behavior across the DB read path. It validates public `Iterator` API semantics, internal `DBIter` reseek and visibility logic, read-tier behavior, iterator bounds, pinning, snapshots, column-family lifetime handling, multi-range scan preparation, async/sync prefetch integration, I/O dispatcher accounting, and read-path conversion of point tombstone runs into redundant range tombstones.

The tests are intentionally integration-heavy: they construct real DB instances through `DBTestBase`, write/flush/compact/ingest SST files, inject `SyncPoint` callbacks, inspect performance/statistics counters, and verify iterator-visible results under many LSM shapes.

## Important APIs, Types, and Fixtures

- `DummyReadCallback` extends `ReadCallback` and treats every sequence as visible while allowing tests to set `max_visible_seq_`; `DBIteratorTest::NewIterator` optionally passes it into `DBImpl::NewIteratorImpl`.
- `DBIteratorBaseTest` derives from `DBTestBase` and names the test DB `db_iterator_test` with fsync enabled.
- `DBIteratorTest` is parameterized by a boolean controlling whether iterators are created with a read callback. Its custom `NewIterator` obtains `ColumnFamilyHandleImpl`, `ColumnFamilyData`, latest/snapshot sequence, a referenced `SuperVersion`, and calls `DBImpl::NewIteratorImpl`.
- `DBIteratorTestForPinnedData` extends `DBIteratorTest` and stress-tests `ReadOptions::pin_data` across randomized puts, deletes, merges, reopen, compaction, and flush patterns.
- `DBMultiScanIteratorTest` is parameterized by `ReadOptions::fill_cache` and tests `DBImpl::NewMultiScan`, `MultiScanArgs`, `MultiScan`, range iteration, prefetch, async I/O, and `TrackingIODispatcher`.
- `NoAsyncIOFS` is a `FileSystemWrapper` that masks `FSSupportedOps::kAsyncIO` and fails the test if async operations are attempted, proving `MultiScan` falls back to sync I/O when async support is absent.
- `ReadPathRangeTombstoneTest` is parameterized by iteration direction and observes `MemTable::AddLogicallyRedundantRangeTombstone:AddRange` to verify read-path point-delete run conversion. Helpers build data with optional user-defined timestamps, assert attempted range endpoints, and iterate forward or backward.
- Helper types and APIs used throughout include `ReadOptions`, `WriteOptions`, `Options`, `BlockBasedTableOptions`, `FlushBlockEveryKeyPolicyFactory`, `MultiScanArgs`, `SstFileWriter`, `IngestExternalFileOptions`, `ManagedSnapshot`, `LiveFileMetaData`, `SuperVersion`, `ColumnFamilyHandleImpl`, `SliceTransform`, `MergeOperators`, `PerfContext`, `Statistics`, and RocksDB `SyncPoint`.

## Control Flow and Coverage Areas

The file starts with base iterator API checks. `APICallsWithPerfContext` verifies `Seek`, `SeekToFirst`, `SeekToLast`, `SeekForPrev`, `Next`, and `Prev` increment the expected `PerfContext` counters. A group of `PrepareWithMultiScan...` tests exercises `Iterator::Prepare(MultiScanArgs)` before normal seeks, ensuring non-intersecting files, levels, L0 files, and memtables are pruned, same-file ranges are deduplicated, unbounded ranges are accepted, and repeated `Prepare` calls fail.

The core `DBIteratorTest` cases then cover:

- empty, single-key, multi-key, large-value, long-key, and delete-containing iteration in both directions;
- snapshot isolation and implicit iterator snapshots when writes happen after iterator creation;
- direction changes between `Next` and `Prev`, including reseek behavior when hidden versions, deletes, or merge operands exceed `max_sequential_skip_in_iterations`;
- `SeekForPrev`, `SeekToLast`, upper/lower bounds, mutable bound slices, prefix extractors, `prefix_same_as_start`, and out-of-domain prefix targets;
- `kBlockCacheTier`, nonblocking iteration, cache-only incomplete status, block cache counters, and a regression where incomplete subiterators formerly skipped records;
- `ReadOptions::table_filter` inclusion/exclusion of SSTs;
- iterator property strings such as `rocksdb.iterator.is-key-pinned`, `rocksdb.iterator.is-value-pinned`, `rocksdb.iterator.internal-key`, `rocksdb.iterator.write-time`, and `rocksdb.iterator.super-version-number`;
- unsupported `kPersistedTier` iterator creation.

Several tests focus on stateful lifetime and refresh paths. Column-family tests destroy or drop CF handles before or after lazy iterator tree materialization and then seek/delete iterators to verify iterator-held references remain valid. `Refresh`, `RefreshWithSnapshot`, `AutoRefreshIterator`, and `IteratorRefreshReturnSV` verify manual and automatic refresh update iterator snapshots/SuperVersions correctly, do not expose writes outside the intended snapshot, and release stale memory/files when possible.

The multi-scan section builds one or more ranges through `MultiScanArgs`, scans via `DBImpl::NewMultiScan`, and catches `MultiScanException`/`logic_error`. It covers mixed bounded/unbounded ranges, ranges crossing or falling between files, L0 range mismatch, fragmented range tombstones, same-user-key reseek across blocks, async prefetch across files and levels, delete ranges, external file ingestion, filesystem async fallback, I/O dispatcher stats, known block prefetch counts, cache-hit tracking, sorted-range avoidance of dispatcher sorting, and wasted prefetch block accounting.

The final major block, `ReadPathRangeTombstoneTest`, validates an optimization that materializes logically redundant range tombstones from long point-tombstone runs seen during reads. It tests forward and reverse iteration, exhausted iterators with and without bounds, direction changes, mixed `Delete`/`SingleDelete`, prefix-filter modes, `total_order_seek`, `prefix_same_as_start`, table-filter rejection, snapshots that predate candidate memtables, `kBlockCacheTier` incomplete reads, existing range tombstone coverage, user-defined timestamp comparators, older timestamp reads that must not materialize unsafe ranges, lower/upper bound endpoint truncation, `SeekForPrev`/`SeekToLast` regressions, invisible keys, externally ingested newer points, and snapshot preservation after redundant range conversion.

## State and Persistence Behavior

Most tests intentionally mutate persistent RocksDB state: they write keys, tombstones, merge operands, flush memtables to SSTs, compact files between levels, move files to exact levels, ingest external SSTs, switch memtables, pause/continue background work, reopen databases, and delete/drop column families. These operations create LSM shapes that force specific iterator subpaths: memtable-only reads, L0 overlapping file reads, non-L0 level iterators, bottom-level files, range deletions, block boundaries, blob files, and cache hits/misses.

Iterator state under test includes:

- current direction and saved key/value state across `Seek`, `SeekForPrev`, `Next`, `Prev`, `SeekToFirst`, and `SeekToLast`;
- snapshot sequence and read callback visibility boundaries;
- SuperVersion references and auto-refresh transitions;
- upper/lower bound pointers, including tests that mutate the bound `Slice` target between seeks;
- pinning state for returned key/value slices under `ReadOptions::pin_data`;
- status propagation from incomplete cache-only reads, unsupported tiers, injected corruption, and retryable I/O errors;
- read-path conversion attempts into the active memtable and associated inserted/discarded counters.

Persistence behavior is verified by reopening after WAL recovery, compaction, external ingestion, and snapshot acquisition. Tests ensure read-path range tombstone insertion does not corrupt older snapshots or hide newer ingested points, and that iterator-held references keep old files/SuperVersions alive only when needed.

## Dependencies and Integration Points

This file depends on RocksDB internal DB test utilities and read-path internals:

- `db/arena_wrapped_db_iter.h`, `db/db_iter.h`, and `db/db_test_util.h` for iterator internals, fixtures, and helpers such as `Put`, `Delete`, `Flush`, `MoveFilesToLevel`, `FilesPerLevel`, `IterStatus`, `VerifyIterLast`, and `ChangeOptions`.
- `env/composite_env_wrapper.h`, `rocksdb/file_system.h`, and `rocksdb/io_dispatcher.h` for filesystem wrapping, async-I/O capability probing, and dispatcher instrumentation.
- `rocksdb/iostats_context.h`, `rocksdb/perf_context.h`, and `Statistics` tickers for local and global read-path metrics.
- `table/block_based/flush_block_policy_impl.h` and `BlockBasedTableOptions` for deterministic data-block layout and cache behavior.
- `utilities/merge_operators/string_append/stringappend2.h` and other `MergeOperators` for merge-operand iterator paths.
- `SyncPoint` integration with internal labels such as `TableCache::NewIterator::BeforeFindTable`, `Version::AddIteratorsForLevel:*`, `MergeIteratorBuilder::Finish:UseMergingIterator`, `RandomAccessFileReader::Read::*`, `ArenaWrappedDBIter::Refresh:SV`, `IODispatcherImpl::SubmitJob:SortBlockHandles`, and `MemTable::AddLogicallyRedundantRangeTombstone:AddRange`.

The tests are compiled into a standalone gtest binary with `main()` installing RocksDB's stack trace handler and running all tests.

## Risks and Fragile Areas

- Many assertions depend on exact ticker counts, block counts, file counts, or SyncPoint callback counts. Changes in block layout, cache policy, flush policy, compaction output, or prefetch heuristics can break tests without user-visible iterator regressions.
- Several tests mutate `ReadOptions` bound slices after iterator creation. This deliberately follows an integration use case, but it means iterator code must continue reading bound pointers dynamically and safely.
- `DBIteratorTest::NewIterator` manually manages read callbacks stored in a vector guarded by a mutex. The iterator does not own those callbacks; lifetime assumptions are critical.
- Range tombstone conversion is high risk because it writes optimization artifacts into the active memtable during reads. The tests explicitly guard snapshot sequence assignment, timestamp visibility, prefix/table-filter safety, incomplete reads, existing range coverage, and external ingestion interactions.
- Async prefetch tests are environment-sensitive. `NoAsyncIOFS` protects fallback behavior, while dispatcher statistic tests allow some variability but still expect nonzero operations and broad minimums.
- Tests using randomized data use fixed seeds, but still cover large data volumes and may be expensive outside normal RocksDB test configurations.
- Some behavior is conditional on table format or options: plain table, hash indexes, merge operators, no-`SeekToLast` modes, mmap reads, and Valgrind configurations are skipped or branched around.

## Test Signals

The strongest signals in this file are:

- exact key/value order from forward and reverse iteration under snapshots, deletes, merges, bounds, prefixes, blobs, and compaction/reopen cycles;
- `Status` checks for `OK`, `Incomplete`, `NotSupported`, `Corruption`, `InvalidArgument`, and injected `IOError`;
- `PerfContext` counters for API calls, skipped internal keys, delete skips, recent-version skips, memtable seek/next/prev counts, and iterator read bytes;
- RocksDB `Statistics` tickers such as `NUMBER_OF_RESEEKS_IN_ITERATION`, `NUMBER_DB_NEXT`, `NUMBER_DB_PREV`, `ITER_BYTES_READ`, `NUMBER_ITER_SKIP`, `READ_PATH_RANGE_TOMBSTONES_INSERTED`, `READ_PATH_RANGE_TOMBSTONES_DISCARDED`, `MULTISCAN_PREFETCH_BLOCKS_WASTED`, and block-cache hit/miss counters;
- SyncPoint callback counts proving iterator construction/pruning paths, async/sync dispatch paths, and range tombstone insertion attempts;
- file-level state checks through `NumTableFilesAtLevel`, `FilesPerLevel`, `GetLiveFilesMetaData`, `GetColumnFamilyMetaData`, and filesystem `FileExists`.

Together, these tests form broad regression coverage for RocksDB iterator correctness, visibility, resource accounting, and read-path optimizations under realistic LSM state transitions.
