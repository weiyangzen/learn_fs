# sources/storage-engines/rocksdb/db/compaction/compaction_iterator_test.cc

## Purpose

`compaction_iterator_test.cc` is the focused unit-test suite for `CompactionIterator` and `CompactionBlobResolver`. It builds synthetic internal-key streams and verifies the exact compaction output for point keys, range tombstones, merges, SingleDelete, snapshot checker behavior, timed puts, user-defined timestamp GC, ingest-behind, compaction filters, wide-column blob extraction, and wide-column blob-reference handling.

The tests are important because `CompactionIterator` is a dense state machine with many cross-cutting conditions. Most tests assert precise output keys and values, which directly captures whether compaction would persist the right table records.

## Important fixtures, helpers, and test doubles

`ValueWithPreferredSeqno` packs a preferred sequence number into a timed-put value. It supports tests for `kTypeValuePreferredSeqno` and preferred sequence swapping.

`NoMergingMergeOp` fails if merge methods are invoked, useful when tests expect merge operands to pass through without actual merging. `SingleMergeOp` verifies partial and full merge paths and supports single operand merging. Several tests use built-in string append merge operators.

`StallingFilter` is a compaction filter that busy-waits on selected keys and always returns remove. It is used to verify shutdown during filter and merge processing. `FilterAllKeysCompactionFilter` returns remove for every filterable key. Later wide-column tests define `KeepAllCompactionFilter` with FilterV4 support and `DropKeyKeepRestCompactionFilter`.

`LoggingForwardVectorIterator` extends `VectorIterator` and records `SeekToFirst`, `Seek`, and `Next`. The skip-until test uses this to verify that compaction filter decisions cause the intended seeks and do not scan extra keys.

`FakeCompaction` implements `CompactionIterator::CompactionProxy` for ordinary tests. It exposes toggles for bottommost level, ingest-behind, lower-level key absence, and per-key placement support. `FakeCompactionWithBlobGC` supports the subset needed by wide-column blob tests while intentionally disabling real blob GC because it has no `Version`.

`TestSnapshotChecker` maps snapshot sequence numbers to last visible sequence numbers and implements `CheckInSnapshot`. This allows tests to model uncommitted data and released/limited visibility without a full transaction DB.

`CompactionIteratorTest` owns the common setup: comparator, internal comparator, snapshots, merge helper, logging iterator, compaction range deletion aggregator, optional snapshot checker, shutdown flag, and `CompactionIterator`. `InitIterators` assembles range tombstone iterators, optional fake compaction, merge helper, input iterator, and the compaction iterator under test. `RunTest` consumes the iterator and compares output sequences.

Specialized fixtures include `CompactionIteratorWithSnapshotCheckerTest`, `CompactionIteratorWithAllowIngestBehindTest`, `CompactionIteratorTsGcTest`, `WideColumnEntityBlobExtractionTest`, and `WideColumnEntityBlobGCTest`.

## Coverage and control flow

The initial parameterized tests cover baseline behavior with and without a snapshot checker. `EmptyResult` verifies SingleDelete plus matching value can compact to no output. `CorruptionAfterSingleDeletion` ensures a corrupt internal key after SingleDelete fails compaction. Timed put compatibility tests show timed puts act like puts for SingleDelete and range deletion in relevant paths.

Range deletion tests create fragmented range tombstone state through `CompactionRangeDelAggregator` and verify covered point keys are dropped while uncovered keys remain. `CompactionFilterSkipUntil` provides a detailed mixed stream of values, merges, timed puts, and skip targets, then checks both output records and the exact underlying iterator actions.

Shutdown tests start compaction in another thread with a stalling filter, set the shutdown flag while the filter is running, and verify the iterator exits with `ShutdownInProgress` and no further filter calls. These tests exercise best-effort cancellation while inside filter and merge helper paths.

Merge tests cover single merge operands, multi-operand partial merges, full merge with a base value, and timed puts losing preferred sequence data when merged into a normal put. Bottommost tests verify sequence-number zeroing, deletion removal, SingleDelete removal, and merge-to-put conversion at the last level.

Snapshot-checker tests verify uncommitted keys are preserved as-is, committed older keys compact normally, and same-snapshot duplicate records are deduplicated for values, timed puts, deletions, merges, SingleDelete, and blob indexes. They also cover cases where bottommost sequence zeroing or deletion removal must not occur because the key is not visible to the earliest snapshot or because an older snapshot still needs a value.

SingleDelete write-conflict tests ensure SingleDeletes can be kept for conflict checking and that the matched value/blob/entity/timed-put record is emitted as `kTypeValue` with an empty payload when the optimization is used. Ingest-behind tests verify a compaction that is nominally bottommost does not assume there will never be future lower-level data.

Timed-put preferred sequence tests verify the conditions for swapping the preferred sequence number: visibility to earliest snapshot, no lower-level entries, and no range tombstone resurfacing after the swap. They cover no-swap and swap cases, including bottommost zeroing.

User-defined timestamp GC tests run with `BytewiseComparatorWithU64TsWrapper`. They validate no-GC when history threshold is absent or keys are newer than the threshold, dropping tombstones and old versions when eligible, merge behavior across timestamp thresholds, rewriting timestamp and sequence to zero at bottommost, and SingleDelete timestamp GC behavior.

Wide-column blob extraction tests create serialized entities, run compaction with `BlobFileBuilder`, and assert large columns are replaced by blob references while smaller columns remain inline. They cover one column, multiple columns, below-threshold no extraction, mixed sizes, and default column extraction.

Wide-column blob-reference tests create V2 entities with blob indices and verify the iterator preserves structure and blob metadata when real GC is not enabled. They also test `CompactionBlobResolver` without a fetcher, the deserialization skip optimization when FilterV4 kept an already-deserialized entity, and reset of `entity_deserialized_` after a filter drops one blob-backed entity before processing the next.

## State and persistence behavior under test

The suite verifies output-state transitions by checking internal key type, sequence number, timestamp, and value bytes. It covers records becoming deletions after filtering, blob or wide-column records becoming empty values in SingleDelete optimization, timed puts becoming regular values after preferred sequence swap or merge, and bottommost keys becoming sequence zero.

The blob extraction fixture uses `MockEnv`, `BlobFileBuilder`, mutable/immutable CF options, and blob file addition vectors. Tests assert blob file additions when extraction should write blob files, and no additions when values are below the threshold.

The wide-column blob GC fixture uses serialized V2 entities with explicit `BlobIndex` metadata. Because it lacks a real `Version`, it does not enable full integrated blob GC; instead it verifies that current iterator deserialization and serialization paths preserve blob references and do not corrupt entity layout.

Sync point callbacks count whether `PrepareOutput` deserializes a wide-column entity or skips because `InvokeFilterIfNeeded` already did it. This provides a regression signal for both performance and stale-state correctness.

## Dependencies and integration points

The tests depend on RocksDB test harness utilities, `VectorIterator`, internal key formatting helpers, `CompactionRangeDelAggregator`, range tombstone iterators, merge operators, mock environment/file system support, blob file builder/addition classes, blob index encoding/decoding, wide-column serialization, sync points, and port threading utilities.

The suite integrates directly with the custom `CompactionProxy` constructor rather than full compaction jobs for most cases. This keeps tests small and targeted but means some production-only integration points, notably real `Version`-based blob GC cutoff computation and real blob fetches from storage, are covered elsewhere.

## Risks and gaps

The tests are comprehensive for deterministic iterator output, but most use synthetic in-memory iterators and fake compaction proxies. Full production interactions with table builders, actual `VersionStorageInfo`, blob file cache, mmap reads, prefetch buffers, and real compaction scheduling are not exercised here.

`FakeCompactionWithBlobGC` explicitly disables integrated blob GC because no real `Version` is available. The wide-column blob GC helper accepts a GC cutoff parameter but does not use it, so these tests are preservation and serialization tests, not full relocation tests. Comments point to broader DB tests for real blob GC coverage.

Threaded shutdown tests use busy-waiting filters, which are effective for deterministic unit testing but can be sensitive to scheduling if reused in slower environments. They do, however, assert the key property that no additional filter calls happen after shutdown is observed.

The timestamp GC tests cover many conditions, but correctness still depends on comparator timestamp extraction and ordering contracts outside this file. Any comparator changes would need broader tests.

## Test signals

Strong signals include exact output key/value assertions in `RunTest`, exact input iterator action logs in `CompactionFilterSkipUntil`, status assertions for corruption and shutdown, blob file addition counts, decoded `BlobIndex` size/file/offset checks, wide-column deserialization checks, and sync-point counters for deserialization caching.

The file's `main` installs the RocksDB stack trace handler and runs all GoogleTests, so the suite is directly executable as a normal RocksDB unit-test binary.
