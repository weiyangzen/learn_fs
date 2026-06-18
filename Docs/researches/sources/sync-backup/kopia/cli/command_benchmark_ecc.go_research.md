# sources/sync-backup/kopia/cli/command_benchmark_ecc.go

## Purpose
ECC benchmark command for repository error-correction providers, measuring encode/decode overhead and printing option strings for repository creation.

## APIs, Types, and Functions
Important APIs include types `commandBenchmarkEcc`, `eccBenchResult`; functions/methods `setup`, `run`, `runBenchmark`; Kingpin command(s) ecc: Run ECC benchmarks; flags block-size: Size of a block to encrypt, repeat: Number of repetitions, parallel: Number of parallel goroutines, print-options: Print out options usable for repository creation.

## Control Flow, State, and Persistence
Control flow registers command(s) ecc: Run ECC benchmarks, binds flags block-size: Size of a block to encrypt, repeat: Number of repetitions, parallel: Number of parallel goroutines, print-options: Print out options usable for repository creation, then runs through a no-repository action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches in-memory benchmark buffers and timing results. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, fmt, math, sort, github.com/alecthomas/units, github.com/kopia/kopia/internal/gather, github.com/kopia/kopia/internal/timetrack, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo/ecc. It integrates with Kopia repository internals such as kopia/internal/gather, kopia/internal/timetrack, kopia/internal/units, kopia/repo/ecc plus external packages context, fmt, math, sort, github.com/alecthomas/units.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
