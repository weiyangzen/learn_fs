# sources/storage-engines/pebble/internal/inflight/in_flight_bench_test.go

## Purpose
`in_flight_bench_test.go` benchmarks the common `Tracker.Start`/`Stop` path under different levels of parallelism.

## Important APIs, Types, And Functions
`BenchmarkTracker` reads `GOMAXPROCS`, runs subbenchmarks for parallelism 1, half-procs, procs, and double-procs, and batches operations through a channel to worker goroutines.

## Control Flow
For each subbenchmark, workers consume batch sizes from a buffered channel, repeatedly call `Start` and `Stop`, and the driver feeds enough batches to perform `b.N * parallelism` operations before waiting on a `sync.WaitGroup`.

## State And Persistence Behavior
Only benchmark-local tracker state is used. No persistent output is produced beyond Go benchmark metrics.

## Dependencies And Integration Points
It depends on `runtime`, `sync`, `fmt`, and `testing`. It is useful for comparing vanilla Go and Cockroach runtime overhead as described in the comment.

## Risks And Edge Cases
The benchmark multiplies operations by parallelism, so interpretation of `ns/op` should consider the benchmark’s custom workload shape. Channel batching reduces channel overhead but still includes some scheduling effects.

## Test Signals
Benchmark output signals contention and per-operation overhead of handle generation, stack capture, map store, and delete under varying concurrency.
