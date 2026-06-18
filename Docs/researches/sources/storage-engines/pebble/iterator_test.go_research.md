# sources/storage-engines/pebble/iterator_test.go

## Purpose
Contains the primary unit, randomized, datadriven, and benchmark coverage for Pebble iterator behavior. It validates visible-key semantics over internal versions, read sampling, table and block-property filtering, seek optimization correctness, mutable indexed-batch refresh, bounds ownership, stats, separated value profiling, range-key masking, prefix seeking, and performance under tombstone-heavy or range-key-heavy workloads.

## Important APIs, Types, And Functions
`testIterator` is a reusable helper for combined internal iterators, verifying ordered output and close-error propagation across fixed and randomized child splits. `TestIterator` builds a synthetic public `Iterator` over a fake internal iterator and `mergingIter`, then uses `testdata/iterator` to test point-key visibility, merges, deletes, bounds, snapshots, and stats.

`minSeqNumPropertyCollector` and `minSeqNumFilter` define a table property and filter used by `TestReadSampling` and `TestIteratorTableFilter`. `iterSeekOptWrapper` counts `TrySeekUsingNext` propagation for `TestIteratorSeekOpt`. `errorSeekIter` injects seek errors for `TestIteratorSeekOptErrors`. `testBlockIntervalMapper` supports block interval filter tests.

Targeted tests include `TestReadSampling`, `TestIteratorTableFilter`, `TestIteratorNextPrev`, `TestIteratorStats`, `TestIteratorSeekOpt`, `TestIteratorSeekOptErrors`, `TestIteratorBlockIntervalFilter`, `TestIteratorRandomizedBlockIntervalFilter`, `TestIteratorGuaranteedDurable`, `TestSetOptionsBatchRefreshSeekGE`, `TestSetOptionsBatchRefreshRand`, `TestIteratorBoundsLifetimes`, `TestIteratorStatsMerge`, `TestIteratorValueRetrievalProfile`, `TestSetOptionsEquivalence`, `TestRangeKeyMaskingRandomized`, and `TestIteratorSeekPrefixGERandomized`.

Helper constructors and formatters include `iterOptionsString`, `newTestkeysDatabase`, `newPointTestkeysDatabase`, `randStr`, `randValue`, `randKey`, `buildFragmentedRangeKey`, `waitForCompactionsAndTableStats`, `withStateSetup`, `populateKeyspaceSetup`, `deleteGapSetup`, and `runBenchmarkQueueWorkload`.

Benchmarks cover basic `SeekGE`/`Next`/`Prev`, sequential `SeekPrefixGE` with and without blooms/tombstones/two-level indexes, bounded seek loops, SeekGE no-op behavior, block-property filters, range-key masking, full scans, `NextPrefix`, combined point/range seek, fragmented range keys, prefix seeks through tombstone-only files, point-deleted swaths, and queue-like delete/append workloads.

## Control Flow
Datadriven tests create or reset in-memory DBs, ingest/build/flush data, create snapshots or iterators with parsed options, and delegate scripted iteration to `runIterCmd`. Synthetic tests construct fake internal iterators directly so they can precisely control internal key order and injected errors.

Read-sampling tests force sampling on every iterator-returned key, inspect per-iterator pending read compactions, close the iterator, and inspect DB-level read-compaction queues. Table-filter tests approximate snapshot-like filtering by collecting minimum sequence numbers into table properties and passing a filter through `IterOptions.PointKeyFilters`.

Seek optimization tests wrap or fake the lower iterator to count flags and inject errors. The batch-refresh tests create indexed batches, mutate them after an iterator is positioned, call `SetOptions`, and compare subsequent seeks/steps against expected keys or a fresh iterator. The randomized batch-refresh counterpart repeats this with random point writes, range deletes, bounds, and absolute positioning operations.

Bounds lifetime tests mutate caller-provided bound slices after `NewIter`, `SetBounds`, `SetOptions`, and `Clone` to prove the iterator copies bounds into owned buffers. `SetOptions` equivalence repeatedly randomizes key types, bounds, and range-key masking, comparing a long-lived iterator after `SetOptions` against a newly constructed iterator for the same operation and state.

Range-key masking randomized tests build two DBs with identical logical point/range-key contents but different layout and filter settings, then scan both with points-and-ranges plus masking and require identical point/range output while ensuring masked points remain hidden. Prefix seek randomized tests build an expected prefix-to-key map by scanning, then verify `SeekPrefixGE` for random prefixes.

## State And Persistence Behavior
Tests mostly use `vfs.NewMem` or crashable in-memory filesystems. They deliberately control flushes, compactions, target file sizes, block sizes, and iterator stack choice to shape LSM layout. Some benchmarks clone filesystem state to isolate subbenchmarks from mutations.

Several tests inspect or mutate internal DB state under locks, including current versions, allowed seek counters, compaction flags, compacting counts, table stats, snapshots, and read-compaction queues. Randomized tests log seeds so failures can be reproduced. Long-lived iterators and batches are closed with defers, and benchmark state helpers close DBs/readers/caches explicitly.

No production data is persisted by these tests, but they validate persistence-adjacent behavior: flush/ingest/compact layout, durable-only reads, table property persistence in sstables, and blob/separated value retrieval profiling.

## Dependencies And Integration Points
The file ties together most of Pebble's iterator stack: `base` fake/internal iterators and stats, `invalidating` wrappers, `iterv2` key generators and trigger paths, `manifest` levels, `testkeys`, `treesteps`, `sstable` readers/writers/block-property collectors/filters, `cache`, `objstorageprovider`, in-memory VFS, datadriven tests, leak testing, `require`, and concurrency helpers.

It relies on shared test helpers such as `runDBDefineCmd`, `runBuildCmd`, `runIngestCmd`, `runLSMCmd`, `runIterCmd`, `printIterState`, `buildMemTable`, `buildLevelsForMergingIterSeqSeek`, and `buildMergingIter` defined elsewhere in the Pebble test suite. Many cases are deliberately end-to-end across DB, Batch, Snapshot, table writing, and iterator construction.

## Risks And Edge Cases
The tests highlight the iterator's riskiest semantics: merge chains mixed with deletes, direction switches, prefix iteration after bloom-filter misses, seek-using-next no-op paths, limits, bounds changes without external repositioning, mutable indexed batches, range deletes added after iterator creation, range-key masking with block filters, and lazy/separated values.

Randomization increases coverage but can introduce nondeterminism, so tests use fixed seeds where needed, log generated seeds elsewhere, disable automatic compactions in layout-sensitive cases, and sometimes set `forceEnableSeekOpt`. Some benchmark fixtures are large and performance-oriented rather than strict correctness checks; they still encode important workload assumptions around tombstone buildup and fragmented range keys.

Direct use of internal fields such as `d.mu`, `iter.forceEnableSeekOpt`, `iter.merging.forceEnableSeekOpt`, and fake iterators makes the tests sensitive to internal refactors. That is intentional for coverage but raises maintenance cost when iterator stack internals change.

## Test Signals
Failure signals are diverse and strong. Datadriven output changes flag visible semantic drift. Randomized equivalence failures indicate `SetOptions`, range-key masking, or batch refresh divergence from fresh iterators. Seek optimization counters and injected errors detect unsafe flag propagation or stale error handling. Stats tests catch accounting regressions. Bounds lifetime tests catch memory aliasing. Benchmarks provide performance regression signals for scans, prefix seeks, filtered iteration, tombstone swaths, queue workloads, and combined point/range iteration.
