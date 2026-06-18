# sources/storage-engines/pebble/sstable/reader_iter_two_lvl_benchmark_test.go

## Purpose
This benchmark file measures construction and first-use behavior for two-level SSTable iterators, with special attention to the lazy top-level index loading optimization. It creates synthetic SSTables large enough to force two-level indexes and compares construction-only, first-access, seek, prefix seek, bloom-filter miss/hit, iterator reuse, concurrent creation, memory allocation, and table-format behavior.

## Important APIs, Types, And Functions
`setupTwoLevelBenchmarkData` builds a 50,000-key table with small block and index block sizes, verifies `AttributeTwoLevelIndex`, and returns the reader and keys. `setupBloomFilterData` builds a bloom-filter-backed two-level table with timestamped `testkeys`. Benchmarks include `BenchmarkTwoLevelIteratorConstruction`, `BenchmarkTwoLevelIteratorFirst`, `BenchmarkTwoLevelIteratorSeekGE`, `BenchmarkTwoLevelIteratorSeekPrefixGE_NoHit`, `BenchmarkTwoLevelIteratorSeekPrefixGE_Hit`, and a set of `BenchmarkTwoLevelLazyLoading*` functions. The table-format benchmark switches between `newRowBlockTwoLevelIterator` and `newColumnBlockTwoLevelIterator` based on `TableFormat.BlockColumnar`.

## Control Flow
Each setup uses in-memory VFS files, writes enough keys to force a two-level index, closes and reopens the table, then creates a `Reader`. Benchmark bodies repeatedly instantiate iterators with `newRowBlockTwoLevelIterator` or `newColumnBlockTwoLevelIterator`, perform the target operation, validate basic non-nil/nil expectations, and close the iterator. Bloom-filter benchmarks use a missing prefix to isolate the path where `SeekPrefixGE` should return nil before index loading. Reuse manually gets a `twoLevelIteratorRowBlocks` from a local `sync.Pool`, initializes the embedded single-level iterator, seeks, closes, resets, and returns it.

## State And Persistence Behavior
The benchmarks persist test SSTables only in `vfs.NewMem`, not on disk. They intentionally measure transient state: lazy `topLevelIndexLoaded`, pool reuse, read-handle setup, bloom-filter state, and allocations. Readers are closed after benchmark cases, while iterators are closed per iteration to include construction teardown behavior in most timings.

## Dependencies And Integration Points
The file uses Pebble's `NewWriter`, `newReader`/`NewReader`, object storage wrappers, `testkeys.Comparer`, `bloom.FilterPolicy`, `base` seek flags, and both row and column two-level constructors. It is an integration benchmark rather than a unit benchmark because it exercises actual writer output, reader metadata, index blocks, filters, and iterator construction paths.

## Risks
The setup assumes specific key counts and block sizes continue to force two-level indexes; writer format changes could make benchmarks fail or skip unexpectedly. Some benchmarks include table creation outside the timed region but still validate each iteration, so they are correctness-aware but not pure microbenchmarks. The manual pool-reuse benchmark has extra reset/put behavior that may not exactly match production pools and could double-reset if iterator close behavior changes.

## Test Signals
Failures indicate a two-level index was not created, expected hits/misses are wrong, or lazy construction no longer supports the benchmarked operation. Allocation reporting in lazy-loading benchmarks is a useful signal for regressions in deferred index loading. Concurrent access uses `b.RunParallel` to expose thread-safety issues in reader-shared state and iterator-local state.
