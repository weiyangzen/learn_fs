# sources/storage-engines/pebble/sstable/tablefilters/internal/filtersim/fpr.go

## Purpose
Provides shared concurrent helpers for estimating and formatting table-filter false-positive rates.

## Important APIs, Types, And Functions
`SimulateFPR(numRuns, avgSize, runExperiment)` executes experiments in parallel and aggregates rates with `metricsutil.Welford`. `FormatFPR` prints a percentage plus 1-in-N ratio. `FormatFPRWithStdDev` adds relative standard deviation formatting.

## Control Flow
`SimulateFPR` preloads a channel with run tokens, starts `GOMAXPROCS` workers, picks a random size within +/-10 percent of average for each run, invokes the caller experiment, and adds the result under a mutex.

## State And Persistence Behavior
No persistent state. The Welford accumulator is transient and protected by a mutex.

## Dependencies And Integration Points
Used by Bloom and binary fuse simulation packages. Depends on `runtime`, `sync`, `math/rand/v2`, `metricsutil`, and `crhumanize`.

## Risks And Edge Cases
`FormatFPR` assumes positive non-zero FPR; zero would produce log/ratio issues. Concurrent simulations share the global random source from `math/rand/v2`.

## Test Signals
No direct tests; correctness is inferred from simulation generators and plausible formatted output.
