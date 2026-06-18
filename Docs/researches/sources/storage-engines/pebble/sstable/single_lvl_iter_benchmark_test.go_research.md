# sources/storage-engines/pebble/sstable/single_lvl_iter_benchmark_test.go

## Purpose
Benchmarks construction and first-positioning operations for row-block single-level SSTable iterators.

## Important APIs, Types, And Functions
Global `benchReader` and `benchIterOpts` are initialized in `init`. Benchmarks include `BenchmarkIteratorConstruction`, `BenchmarkIteratorFirst`, `BenchmarkIteratorSeekGE`, `BenchmarkIteratorSeekPrefixGE_Hit`, and `BenchmarkIteratorSeekPrefixGE_NoHit`.

## Control Flow And State
The `init` function builds an in-memory Pebblev3 SSTable with 10,000 ordered keys, 4 KiB data and index blocks, Bloom filter policy, default comparer, and default merger. It opens a reader and prepares iterator options with a block buffer pool and trivial reader provider. Each benchmark constructs `newRowBlockSingleLevelIterator`; some time only construction, while others stop the timer around setup and measure `First`, `SeekGE`, or `SeekPrefixGE` with filter enabled for hit/no-hit cases.

## Persistence And Integration
The benchmark stores its SSTable in `vfs.NewMem` and keeps a reader alive globally for repeated benchmark iterations. It integrates the row-block writer, table reader, block cache/buffer environment, Bloom filters, and single-level row-block iterator path.

## Risks
Because setup happens in package init and uses a fixed synthetic dataset, benchmark representativeness is limited to sorted short keys and Pebblev3 row blocks. The global reader is not closed, which is acceptable for process-lifetime benchmarks but not a production pattern. Benchmark results are sensitive to filter settings and buffer pool behavior.

## Test Signals
This file provides performance regression signal for iterator construction, first access, point seek, and prefix seek with Bloom-filter hit and miss behavior. It is not a correctness test.
