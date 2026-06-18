# sources/sync-backup/kopia/cli/command_benchmark_hashing.go

## Purpose
Hashing benchmark command for content hash algorithms, reporting throughput and option strings for repository creation.

## APIs, Types, and Functions
Important APIs include types `commandBenchmarkHashing`; functions/methods `setup`, `run`, `runBenchmark`; Kingpin command(s) hashing: Run hashing function benchmarks; flags block-size: Size of a block to hash, repeat: Number of repetitions, parallel: Number of parallel goroutines, print-options: Print out options usable for repository creation.

## Control Flow, State, and Persistence
Control flow registers command(s) hashing: Run hashing function benchmarks, binds flags block-size: Size of a block to hash, repeat: Number of repetitions, parallel: Number of parallel goroutines, print-options: Print out options usable for repository creation, then runs through a no-repository action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches in-memory benchmark buffers and timing results. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, sort, github.com/alecthomas/units, github.com/kopia/kopia/internal/gather, github.com/kopia/kopia/internal/timetrack, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo/format, github.com/kopia/kopia/repo/hashing. It integrates with Kopia repository internals such as kopia/internal/gather, kopia/internal/timetrack, kopia/internal/units, kopia/repo/format, kopia/repo/hashing plus external packages context, sort, github.com/alecthomas/units.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
