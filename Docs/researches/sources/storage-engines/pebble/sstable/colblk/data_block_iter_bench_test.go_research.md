<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block_iter_bench_test.go -->
# sources/storage-engines/pebble/sstable/colblk/data_block_iter_bench_test.go

## Purpose
`data_block_iter_bench_test.go` benchmarks hot `DataBlockIter` operations on a realistic columnar data block containing many versions per prefix. It is performance instrumentation rather than correctness coverage.

## Important APIs, Types, And Functions
The file defines `BenchmarkDataBlockIter`. It builds a roughly 32 KiB block using `DataBlockEncoder`, `DefaultKeySchema`, and `NoTieringColumns`, then benchmarks `SeekGE`, `SeekPrefixGE`, `SeekGE` with `TrySeekUsingNext`, `Next`, and `Prev`.

## Control Flow
The setup writes numeric prefixes with ten MVCC-style suffix versions each, in reverse timestamp order to satisfy the comparer ordering. It finishes the block, initializes `DataBlockDecoder`, constructs one `DataBlockIter`, and reuses it across benchmark subtests. Random-seek benchmarks use a deterministic shuffled prefix slice. The `TrySeekUsingNext` benchmark walks prefixes monotonically and uses a plain `SeekGE` only when wrapping to the beginning.

## State And Persistence Behavior
The benchmark creates one persisted block byte slice in memory and then repeatedly exercises iterator state over that decoded block. It does not touch disk. The benchmark's useful state is the row distribution: repeated prefixes with multiple suffixes exercise prefix-change bitmap and suffix-seek logic.

## Dependencies And Integration Points
The benchmark depends on `testkeys.Comparer`, `block.InPlaceValuePrefix`, `blockiter.Transforms`, and the shared `testKeysSchema` from `data_block_test.go`. It gives performance feedback for the same methods used by higher-level SSTable iterators.

## Risks
Because one iterator is reused inside each sub-benchmark, measurements reflect realistic stateful iteration but may hide costs of repeated initialization. It uses no transforms, obsolete hiding, external values, or tiering metadata, so it does not measure those cold paths.

## Test Signals
The benchmark can detect regressions in seek and step performance. It is not a pass/fail correctness test beyond requiring setup and iterator operations not to panic.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block_iter_bench_test.go -->
