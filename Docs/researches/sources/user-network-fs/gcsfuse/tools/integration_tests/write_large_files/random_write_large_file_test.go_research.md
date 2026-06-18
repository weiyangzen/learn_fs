# sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/random_write_large_file_test.go

Purpose: integration test for random offset writes into a large sparse file through gcsfuse.

Important APIs/types/functions: `TestWriteLargeFileRandomly`, `NumberOfRandomWriteCalls`, `DirForRandomWrite`, and `MaxFileOffset`.

Control flow: opens a local and mounted file, performs 20 random writes of `ChunkSize` bytes below 500 MiB, aligns offsets to 4 KiB for `O_DIRECT`, writes identical chunks to both files, closes them, and compares content.

State/persistence behavior: creates local temp state and a mounted object with random sparse writes. Content is persisted through close/sync behavior in helpers.

Dependencies/integration: uses `internal/cache/util.KiB` for alignment and shared write-large-file constants.

Risks/test signals: randomness means coverage varies by run; it validates final content equivalence rather than specific offsets. Sparse-file semantics and direct I/O alignment are important.
