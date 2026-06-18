# sources/storage-engines/pebble/sstable/rowblk/rowblk_bench_test.go

## Purpose
This file benchmarks row-block iterator operations with and without synthetic prefixes and suffixes. It focuses on the lower-level block iterator used by SSTable readers, measuring `SeekGE`, `SeekLT`, `Next`, and `Prev` over a generated block.

## Important APIs, Types, And Functions
Global benchmark constants define `benchSynthSuffix`, `benchPrefix`, and `benchComparer`. `chooseOrigSuffix` randomly selects an original suffix of different lengths so suffix replacement can grow keys. `createBenchBlock` fills a row-block `Writer` until a target size, returns the keys expected to be visible to the reader, and returns synthetic prefix/suffix settings. Benchmarks instantiate `NewIter` with `blockiter.MakeSyntheticPrefixAndSuffix` and run the target operation in nested cases for synthetic prefix on/off, synthetic suffix on/off, and restart interval.

## Control Flow
Each benchmark builds one 32 KiB block per subcase, creates a row-block iterator with the selected transforms, resets the timer, then loops over random seeks or repeated directional stepping. Seek benchmarks optionally validate exact key matches under verbose mode when no synthetic suffix changes expected ordering. Directional benchmarks restart at `First` or `Last` when the iterator becomes invalid.

## State And Persistence Behavior
The benchmarks are entirely in memory. The row-block byte slice is produced by `Writer.Finish`; iterator state is reused across loop iterations. Randomness comes from a PCG seeded with current time, so exact key sequence differs by run but benchmark shape is stable.

## Dependencies And Integration Points
The file depends on row-block `Writer`/`NewIter`, `testkeys.Comparer` for MVCC-like suffix ordering, `base` seek flags, and `blockiter.Transforms`. It provides lower-level performance context for reader-level benchmarks that also use synthetic prefix/suffix transforms.

## Risks
Because the RNG seed includes wall-clock time, microbenchmark results can vary slightly across runs. Verbose-only assertions mean normal benchmark runs mainly measure performance, not exhaustive correctness. The benchmark currently tests only restart interval 16, so it does not characterize all restart configurations.

## Test Signals
Allocation or latency changes in these benchmarks can signal regressions in synthetic prefix/suffix handling, restart search, or directional stepping. Unexpected verbose-mode failures would indicate transform or comparator incompatibility in the block iterator.
