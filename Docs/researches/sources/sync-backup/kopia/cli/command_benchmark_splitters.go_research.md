# sources/sync-backup/kopia/cli/command_benchmark_splitters.go

## Purpose
Splitter benchmark command that generates deterministic random data and measures dynamic content splitter throughput, chunk counts, and fastest option selection.

## APIs, Types, and Functions
Important APIs include types `commandBenchmarkSplitters`; functions/methods `setup`, `run`; Kingpin command(s) splitter: Run splitter benchmarks; flags rand-seed: Random seed, data-size: Size of a data to split, block-count: Number of data blocks to split, print-options: Print out the fastest dynamic splitter option, parallel: Number of parallel goroutines.

## Control Flow, State, and Persistence
Control flow registers command(s) splitter: Run splitter benchmarks, binds flags rand-seed: Random seed, data-size: Size of a data to split, block-count: Number of data blocks to split, print-options: Print out the fastest dynamic splitter option, parallel: Number of parallel goroutines, then runs through a no-repository action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches in-memory benchmark buffers and timing results. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, math, math/rand, sort, strings, time, github.com/alecthomas/units, github.com/pkg/errors, github.com/kopia/kopia/internal/timetrack, github.com/kopia/kopia/internal/units, plus 1 more. It integrates with Kopia repository internals such as kopia/internal/timetrack, kopia/internal/units, kopia/repo/splitter plus external packages context, math, math/rand, sort, strings, plus 3 more.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
