# sources/storage-engines/rocksdb/memtable/memtablerep_bench.cc

## Purpose
`memtablerep_bench.cc` is a gflags-driven microbenchmark for comparing RocksDB `MemTableRep` implementations under fill, point-read, scan, and mixed read/write workloads.

## Important APIs, Types, and Functions
- Flags select benchmark names, memtable representation, bucket counts, skiplist height/branching, hash linked-list thresholds, write buffer size, thread counts, operation counts, item size, prefix length, vector reserve count, and random seed.
- `RandomGenerator` provides deterministic reusable value bytes.
- `KeyGenerator` supports sequential, random, and unique-random write modes.
- `BenchmarkThread` is the base class for fill, concurrent fill, random read, sequential scan, concurrent random read, and concurrent scan workers.
- `Benchmark` runs workers, measures elapsed time with `StopWatchNano`, and prints throughput.
- `main()` creates the selected `MemTableRepFactory`, constructs an arena-backed memtable rep, and dispatches comma-separated benchmarks.

## Control Flow
When gflags is unavailable, the file builds a stub `main()` that asks the user to install gflags. Otherwise, `main()` parses flags, selects a memtable factory (`skiplist`, `vector`, `hashskiplist`/`prefix_hash`, `hashlinklist`/`hash_linkedlist`, or config-string factory), then iterates over benchmark names.

Fill workers allocate encoded memtable entries using `MemTableRep::Allocate`, encode a length-prefixed 16-byte internal key containing user key and incremented sequence, copy a value payload, and call `Insert`. Read workers build `LookupKey` objects and call `Get` with a callback that checks user-key equality. Sequential readers create an iterator and scan from first to last. Mixed read/write runs one writer while the remaining threads read until completion.

## State and Persistence Behavior
Benchmarks use an in-memory `Arena`, `WriteBufferManager`, and `MemTableRep`; there is no DB persistence. Each fill or mixed benchmark resets the memtable rep and sequence counter. Shared counters for bytes and hits are plain integers passed to threads, so metrics are approximate under concurrency.

## Dependencies and Integration Points
The benchmark exercises production memtable factories, `InternalKeyComparator`, `SliceTransform`, `WriteBufferManager`, port threads, system clock, and RocksDB config-string factory parsing. It is also connected to the microbench CMake file, which discovers and builds microbenchmark executables.

## Risks and Test Signals
This is benchmark code, not a correctness test. Concurrent byte counters and sequence increments are not synchronized, and the mixed workload intentionally focuses on throughput rather than exact metrics. Prefix hash reps require a fixed prefix extractor configured in this file. Useful signals are relative throughput, scan cost, and workload sensitivity across representations.
