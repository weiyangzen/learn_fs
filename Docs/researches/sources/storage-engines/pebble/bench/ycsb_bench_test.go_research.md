# sources/storage-engines/pebble/bench/ycsb_bench_test.go

## Purpose
`ycsb_bench_test.go` provides an in-process Go benchmark mirroring a Pebble YCSB roachtest. It builds/reuses large fixtures and runs workloads A-F with profiler-friendly local execution.

## Important APIs, Types, And Functions
`BenchmarkYCSB`, `ycsbBenchSizes`, flags `ycsb-bench-fixture-dir` and `ycsb-bench-initial-keys`, `defaultYCSBFixtureDir`, `ensureYCSBFixture`, and `runYCSBWorkload` are the major pieces.

## Control Flow
`BenchmarkYCSB` iterates value sizes 64 and 1024, derives a fixture path by value size, key count, and format version, ensures the fixture exists, then runs workloads A-F. `ensureYCSBFixture` checks a `.ready` marker, removes incomplete fixture state, creates parent directories, loads initial keys through `newYcsb.init`, closes the DB, and writes the marker. `runYCSBWorkload` checkpoints the fixture into `b.TempDir`, opens the checkpoint, configures workload/key distribution/operation cap, starts workers, and waits for them to finish under benchmark timing.

## State And Persistence Behavior
The benchmark may create a multi-gigabyte fixture cache under the user's cache directory by default. The `.ready` marker is the persistence guard against reusing partial fixtures. Each workload uses a hard-linked Pebble checkpoint in a temporary directory to avoid mutating the cached fixture.

## Dependencies And Integration Points
It uses `testing.B`, Pebble checkpointing through `pebbleDB`, `base.NoopLoggerAndTracer`, `randvar`, YCSB helpers, and filesystem flags. It relies on `NewPebbleDB` settings matching the benchmark suite.

## Risks And Edge Cases
The default 10 million key fixture is expensive in disk and time. Hard-link checkpoint behavior depends on filesystem support through Pebble. If a process dies after fixture load but before marker creation, the next run rebuilds. Workload workers may overshoot `b.N` slightly because the stop condition is atomic and checked after operations.

## Test Signals
This is a benchmark, not a normal unit test. Signal is benchmark throughput by workload/value size and the ability to reuse fixtures reproducibly.
