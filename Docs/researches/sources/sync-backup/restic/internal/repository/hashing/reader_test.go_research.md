## sources/sync-backup/restic/internal/repository/hashing/reader_test.go

Purpose: validates and benchmarks `hashing.Reader`.

Important tests: `TestReader` generates random data for several sizes, computes expected SHA-256, copies through `NewReader` to discard, checks byte count and resulting hash. `BenchmarkReader` repeats the same pattern for a 4 MiB buffer.

Control flow and state: each case creates a fresh hash and reader, so accumulated state is isolated.

Dependencies and integration points: verifies behavior used by repository checker streaming hash verification.

Risks and test signals: tests cover full successful reads, not underlying readers that return data plus errors or short reads across many calls.
