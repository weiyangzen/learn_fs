# sources/storage-engines/pebble/bench/bench.go

## Purpose
`bench.go` defines shared benchmark configuration and execution loops for Pebble command-line benchmarks. It abstracts DB-backed and non-DB benchmarks, handles duration/size/signal termination, periodic reporting, optional compaction waiting, and profiler rotation.

## Important APIs, Types, And Functions
`CommonConfig` holds knobs shared by workloads: cache size, concurrency, WAL disabling, duration, max size, verbose logging, wipe behavior, shared-storage options, ballast, auto-compaction disabling, rate limiter, and logger. `Test` and `TestWithoutDB` package workload callbacks. `RunTest`, `RunTestWithoutDB`, `startCPUProfile`, and `startRecording` are the core functions. `wait` applies optional rate limiting.

## Control Flow
`RunTest` optionally wipes the directory, opens a DB through `NewPebbleDB`, runs `Init`, starts worker goroutines through `Run`, and enters a select loop over a one-second ticker, worker completion, and interrupt/timeout signals. It prints metrics periodically, stops on `MaxSize`, and may wait for background compactions after workers finish. `RunTestWithoutDB` mirrors this for filesystem benchmarks. CPU profiling rotates every 10 seconds and finalizers write heap and mutex profiles.

## State And Persistence Behavior
This file creates, opens, and may delete benchmark directories. Profiling emits `cpu.*.prof`, `heap.prof`, and `mutex.prof` in the current directory. It does not directly mutate Pebble data beyond delegating to workload callbacks and `NewPebbleDB`.

## Dependencies And Integration Points
It depends on `pebble`, `internal/rate`, `runtime/pprof`, OS signals, and the `DB` abstraction from `db.go`. All workload files call into `RunTest` or `RunTestWithoutDB`.

## Risks And Edge Cases
Risks include unbounded long-running goroutines if a workload never exits, process-level `log.Fatal` in profile setup, profile file churn, and `MaxSize` polling lag. `signal.Notify` is not stopped, which is acceptable for benchmark processes but would be undesirable in reusable libraries.

## Test Signals
There are no direct tests in this file. Coverage is indirect through benchmark commands and workload-specific tests.
