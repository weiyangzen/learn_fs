# sources/sync-backup/kopia/cli/command_benchmark.go

## Purpose
Benchmark command root and shared parallel execution helpers. It registers benchmark subcommands and provides worker fan-out helpers plus reusable output buffers for crypto-style benchmarks.

## APIs, Types, and Functions
Important APIs include types `commandBenchmark`, `cryptoBenchResult`; functions/methods `setup`, `runInParallelNoInputNoResult`, `runInParallelNoInput`, `runInParallelNoResult`, `runInParallel`, `makeOutputBuffers`; Kingpin command(s) benchmark: Commands to test performance of algorithms..

## Control Flow, State, and Persistence
Control flow registers command(s) benchmark: Commands to test performance of algorithms., then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches in-memory benchmark buffers and timing results. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, sync. It integrates with shared CLI infrastructure plus external packages bytes, sync.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. nearby test file `sources/sync-backup/kopia/cli/command_benchmark_test.go` provides direct coverage.
