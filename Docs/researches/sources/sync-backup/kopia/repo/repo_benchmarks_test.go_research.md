# sources/sync-backup/kopia/repo/repo_benchmarks_test.go

Purpose: benchmarks repository object writing with and without deduplication.

Important APIs/types/functions: `BenchmarkWriterDedup1M` writes the same 4 MiB zero buffer repeatedly. `BenchmarkWriterNoDedup1M` writes moving slices of random data to reduce deduplication. Both use `repotesting.NewEnvironment`, `RepositoryWriter.NewObjectWriter`, and object `Result`.

Control flow: the dedup benchmark primes the repository with one object, then repeatedly writes identical data in `b.Loop()`. The no-dedup benchmark fills a random buffer, resets timer, and writes shifting chunks, changing chunk size when the moving window reaches the buffer end.

State and persistence behavior: benchmarks create a test repository and persist object contents and indexes through normal repository paths. Writers are closed after results to return splitters/resources.

Dependencies/integration: integrates object writer, repository write manager, content deduplication, format v2, random data generation, and `testify/require`.

Risks: benchmark naming says `1M` but buffers are 4 MiB; no-dedup chunk-size mutation may create variable object sizes over time. Results can be sensitive to test storage backend and compression/metadata behavior.

Test signals: benchmark-only; useful for performance regressions in write/dedup paths, not correctness gates.
