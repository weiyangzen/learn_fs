## sources/sync-backup/restic/internal/repository/hashing/writer_test.go

Purpose: validates and benchmarks `hashing.Writer`.

Important tests: `TestWriter` writes random buffers of several sizes through `NewWriter(io.Discard, sha256.New())`, checks copied byte count, and compares hash with direct SHA-256. `BenchmarkWriter` measures hashing write throughput for a 4 MiB buffer.

Control flow and state: each iteration uses a fresh writer and hash.

Dependencies and integration points: protects streaming hash behavior used by repository write paths.

Risks and test signals: tests do not simulate partial writes or underlying writer errors.
