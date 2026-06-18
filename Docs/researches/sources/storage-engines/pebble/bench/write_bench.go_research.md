# sources/storage-engines/pebble/bench/write_bench.go

## Purpose
`write_bench.go` implements an adaptive write-throughput benchmark that searches for sustainable insert rates based on L0 file/sublevel thresholds, stalls, and actual-vs-desired rate dips.

## Important APIs, Types, And Functions
`WriteBenchConfig`, `DefaultWriteBenchConfig`, `writeBenchResult`, `RunWriteBench`, `pauseWriter`, and `newPauseWriter` are central. Defaults mirror Cockroach admission-control L0 limits.

## Control Flow
`RunWriteBench` builds a YCSB insert-only workload, starts `pauseWriter` goroutines under rate limiters, and on each tick reads Pebble metrics. Passing a test period increases desired rate exponentially by streak; failure records the rate, backs off to the previous stack entry, pauses writers for a cooloff period, then resumes. Failure is triggered by zero actual rate while not cooling off, L0 file/sublevel limits, or sustained rate dip above the configured fraction.

## State And Persistence Behavior
The benchmark writes real Pebble data through YCSB insert operations. Internal state tracks desired rate, pass/fail history, current cooloff, writer goroutines, and accumulated operation histograms. It does not clean DB state between rate attempts within one run.

## Dependencies And Integration Points
It depends on `ycsb.go`, `ackseq`, `randvar`, `rate`, `RunTest`, and Pebble metrics. It composes with `CommonConfig` but uses its own `Concurrency` field for writer count.

## Risks And Edge Cases
The pause protocol uses unbuffered channels and assumes callers pause/unpause each writer coherently; misuse can block. Search logic can terminate when no backtrack room remains. Metrics thresholds are workload- and option-sensitive, so pass/fail is not portable across hardware. `rateAcc` approximates actual throughput by summing tick rates and may be noisy.

## Test Signals
No direct tests. Benchmark output lines include raw result records and periodic L0/write-amp metrics.
