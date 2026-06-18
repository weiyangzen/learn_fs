# sources/storage-engines/rocksdb/db/range_del_aggregator_bench.cc

## Purpose

`range_del_aggregator_bench.cc` is a gflags-based microbenchmark for range tombstone fragmentation, aggregator insertion, and `ShouldDelete` lookup cost. It can benchmark either `ReadRangeDelAggregator` or `CompactionRangeDelAggregator` over randomly generated tombstones.

## Important APIs, Types, and Functions

The benchmark exposes flags for tombstone count, run count, random seed, key-space bounds, tombstone width distribution, number of `ShouldDelete` calls per run, number of `AddTombstones` batches per run, and whether to use the compaction aggregator. `Stats` records nanoseconds spent in fragmentation, `AddTombstones`, first `ShouldDelete`, and later `ShouldDelete` calls. `PersistentRangeTombstone` owns backing strings for `RangeTombstone` slices. `MakeRangeDelIterator` serializes tombstones into a `VectorIterator`, and `Key()` encodes integers as big-endian fixed-width strings so lexicographic bytewise order matches numeric order.

## Control Flow and State Behavior

For each run, the benchmark constructs a fresh aggregator and a vector of fragmented tombstone lists. Each batch fills `FLAGS_num_range_tombstones` with random starts and normally distributed widths, serializes them, times `FragmentedRangeTombstoneList` construction, creates a `FragmentedRangeTombstoneIterator`, and times `AddTombstones`. It then creates a `ParsedInternalKey` at the midpoint sequence and performs one or more forward `ShouldDelete` calls over adjacent generated keys, separating the first lookup from subsequent lookups to show cache warm-up effects.

When compaction mode is enabled, the benchmark uses `CompactionRangeDelAggregator` with a snapshot vector containing `0`; otherwise it uses `ReadRangeDelAggregator` with `kMaxSequenceNumber`.

## Persistence, Dependencies, and Integration

The file has no persistence behavior; it is a standalone executable. It depends on gflags, `SystemClock`, `Random64`, `StopWatchNano`, `VectorIterator`, internal key serialization, and the range tombstone aggregator/fragmenter code under test.

## Risks and Test Signals

The benchmark is performance signal only, not correctness coverage. Because tombstones are regenerated inside the timed loop, comments note possible cache-warming artifacts. The workload uses forward traversal only and bytewise keys only, so it does not measure reverse scans, timestamp comparators, file-boundary truncation, or realistic table-reader lifetimes. Useful signals are relative timings for fragmentation, add cost, first lookup, and cached subsequent lookups under controlled flag changes.
