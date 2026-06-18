# sources/storage-engines/pebble/sstable/tablefilters/internal/filtertestutils/bench.go

## Purpose
Provides reusable benchmark harnesses for table filter writers and membership checks across Bloom and binary fuse implementations.

## Important APIs, Types, And Functions
`BenchmarkWriter`, `BenchmarkMayContain`, `BenchmarkMayContainLarge`, and `randKeys` are the main helpers. They accept `base.TableFilterPolicy` and decoder interfaces.

## Control Flow
Writer benchmarks generate fixed random key sets for key lengths 6, 16, and 128 and counts 10K, 100K, and 1M, then repeatedly construct filters. Membership benchmarks build a filter, run positive and negative subbenchmarks, and large benchmarks prebuild 1024 large filters then query them with configurable goroutine counts.

## State And Persistence Behavior
All state is in-memory random keys and filter bytes. `crypto/rand` fills key buffers, and benchmark loops report derived throughput metrics.

## Dependencies And Integration Points
Used by Bloom and binary fuse benchmark files. Depends on Pebble base filter interfaces, `crhumanize`, `runtime`, and synchronization primitives.

## Risks And Edge Cases
Large benchmarks allocate substantial memory and are intended for explicit benchmark runs. Positive benchmark indexing assumes at least 4096 keys in the generated set, which holds for configured counts.

## Test Signals
Benchmark output reports MKeys/s or ns/op; fatal checks catch unexpected false negatives or filter build failures.
