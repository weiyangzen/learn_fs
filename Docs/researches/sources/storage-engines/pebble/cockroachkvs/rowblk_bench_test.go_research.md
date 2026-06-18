<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/rowblk_bench_test.go -->
# sources/storage-engines/pebble/cockroachkvs/rowblk_bench_test.go

## Purpose
Benchmarks legacy row-block writer and iterator behavior with Cockroach keys, providing a comparison point for columnar block benchmarks.

## Important APIs, Types, and Functions
`BenchmarkCockroachDataRowBlockWriter`, `benchmarkCockroachDataRowBlockWriter`, `BenchmarkCockroachDataRowBlockIter`, and `benchmarkCockroachDataRowBlockIter` use shared `benchConfigs`, `RandomKVs`, `rowblk.Writer`, and `rowblk.Iter`.

## Control Flow
Writer benchmarks reset a row-block writer with restart interval 16, add generated internal keys and values until target block size, and finish. Iterator benchmarks prebuild one block, initialize a row-block iterator with `Compare`, `ComparePointSuffixes`, and `Split`, then time `Next` loops and random exact `SeekGE` calls.

## State and Persistence Behavior
All benchmark state is in memory. The serialized row block represents persisted block bytes for performance measurement only.

## Dependencies and Integration Points
Depends on `rowblk`, Pebble internal base keys, block value-prefix handling, blockiter transforms, shared Cockroach key generation and benchmark configs from other test files.

## Risks and Edge Cases
Seeds use current time, so generated distributions vary. The benchmarks validate `SeekGE` does not return nil for sampled existing keys but are not full correctness tests. Comparisons with columnar benchmarks should account for different writer/iterator implementations and included work.

## Test Signals
Signals are benchmark timings and `bytes/row` metrics for row-block write, scan, and seek paths under Cockroach key distributions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/rowblk_bench_test.go -->
