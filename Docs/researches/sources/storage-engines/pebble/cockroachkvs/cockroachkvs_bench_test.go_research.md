<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/cockroachkvs_bench_test.go -->
# sources/storage-engines/pebble/cockroachkvs/cockroachkvs_bench_test.go

## Purpose
Benchmarks Cockroach key schema performance in SSTable seeking, columnar data-block writing, data-block iteration/seeking, transform handling, and block metadata initialization.

## Important APIs, Types, and Functions
`BenchmarkRandSeekInSST` compares table formats v4-v7 and single/two-level indexes. `benchmarkRandSeekInSST` writes an in-memory SSTable with `Comparer` and `KeySchema`, warms cache, and repeatedly creates iterators and seeks random query keys. `BenchmarkCockroachDataColBlockWriter`, `BenchmarkCockroachDataColBlockIter`, `BenchmarkCockroachDataColBlockIterTransforms`, `benchmarkCockroachDataColBlockIter`, `benchConfigs`, and `BenchmarkInitDataBlockMetadata` exercise columnar block encoding and iteration.

## Control Flow
Benchmarks generate random keys/values with `RandomKVs`, encode blocks or SSTables, optionally warm block cache, reset timers, and repeatedly perform writer finish, iterator `Next`, iterator `SeekGE`, or metadata init. Transform benchmarks cover synthetic sequence numbers, hiding obsolete points, synthetic prefixes, and synthetic suffixes.

## State and Persistence Behavior
All state is in-memory: `objstorage.MemObj`, cache handles sized to fit objects, random generated blocks, and iterator state. Benchmarks report custom `bytes/row` metrics for block iteration cases.

## Dependencies and Integration Points
Depends on SSTable writer/reader, cache, block reader options, internal cache options, `colblk`, blockiter transforms, random key utilities from `test_utils.go`, and helper `generateDataBlock`/`randomQueryKeys` from tests.

## Risks and Edge Cases
Seeds use current time or random values, so benchmark data varies between runs. Iterator creation is inside the `BenchmarkRandSeekInSST` timed loop, so results include construction cost. The benchmark validates some invariants, but it is performance-focused rather than exhaustive correctness coverage.

## Test Signals
Signals are benchmark throughput and `bytes/row` metrics, plus no failures while seeking latest keys when obsolete points are not hidden. These benchmarks can detect regressions in key schema encoding, seeking, and metadata initialization costs.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/cockroachkvs_bench_test.go -->
