<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/lru/lru_benchmark_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/lru/lru_benchmark_test.go

## Purpose
This file defines performance benchmarks for the generic LRU cache. It measures common operations, concurrent mixed workloads, and large-scale prefix deletion scenarios relevant to file and metadata cache invalidation.

## Important benchmarks
`BenchmarkInsert` measures repeated insertions with unique keys. `BenchmarkLookUp` prepopulates 10,000 entries and measures repeated hits. `BenchmarkErase` measures erase cost while excluding setup insertion from the timer. `BenchmarkConcurrency` uses `RunParallel` with 30 percent inserts, 60 percent lookups, and 10 percent erases over a random key space. `BenchmarkInsert1Million` and `BenchmarkEraseEntriesWithGivenPrefix_1Million` exercise very large maps/lists.

## Control flow and state behavior
The benchmarks use the `testData` `ValueType` from `lru_test.go`. Large benchmarks recreate the cache inside each iteration with timers stopped, then measure the specific operation under test. Prefix deletion benchmark inserts one million entries with half under `prefix/` and times `EraseEntriesWithGivenPrefix("prefix/")`.

## Dependencies and integration points
The file depends on Go `testing`, `fmt`, `math/rand`, `time`, and the production `lru` package. The benchmark for prefix erase directly reflects metadata and file-cache invalidation workloads where many keys share a path prefix.

## Risks and edge cases
`BenchmarkConcurrency` seeds each goroutine's random source with `time.Now().UnixNano`, so repeated workers can occasionally share seeds if started very close together, though this is acceptable for benchmark variability. The million-entry benchmarks are memory-heavy and may be unsuitable for constrained CI by default. Benchmarks do not report allocations explicitly beyond standard Go benchmark output.

## Test signals
These are performance signals rather than correctness tests. They indicate whether changes to locking, list/index maintenance, or prefix scan logic materially affect common and large-scale cache operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/lru/lru_benchmark_test.go -->
