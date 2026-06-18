# sources/sync-backup/kopia/cli/command_benchmark_compression.go

## Purpose
Compression benchmark command for measuring Kopia compression algorithms over generated or file-provided data, including compression, decompression, stability verification, sorting, and option-printing.

## APIs, Types, and Functions
Important APIs include types `commandBenchmarkCompression`, `compressionBenchmarkResult`; functions/methods `setup`, `readInputFile`, `shouldIncludeAlgorithm`, `run`, `runCompression`, `runDecompression`, `sortResults`, `printResults`, `hashOf`; Kingpin command(s) compression: Run compression benchmarks; flags repeat: Number of repetitions, data-file: Use data from the given file, by-size: Sort results by size, by-alloc: Sort results by allocated bytes, parallel: Number of parallel goroutines, operations: Operations, verify-stable: Verify that compression is stable, print-options: Print out options usable for repository creation, deprecated: Included deprecated compression algorithms, algorithms: Comma-separated list of algorithms to benchmark.

## Control Flow, State, and Persistence
Control flow registers command(s) compression: Run compression benchmarks, binds flags repeat: Number of repetitions, data-file: Use data from the given file, by-size: Sort results by size, by-alloc: Sort results by allocated bytes, parallel: Number of parallel goroutines, operations: Operations, verify-stable: Verify that compression is stable, print-options: Print out options usable for repository creation, plus 2 more, then runs through a no-repository action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches in-memory benchmark buffers and timing results. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, context, hash/fnv, io, os, runtime, sort, strings, github.com/pkg/errors, github.com/kopia/kopia/internal/gather, plus 3 more. It integrates with Kopia repository internals such as kopia/internal/gather, kopia/internal/timetrack, kopia/internal/units, kopia/repo/compression plus external packages bytes, context, hash/fnv, io, os, plus 4 more.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
