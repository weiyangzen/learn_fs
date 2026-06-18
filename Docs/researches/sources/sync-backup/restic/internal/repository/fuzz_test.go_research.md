## sources/sync-backup/restic/internal/repository/fuzz_test.go

Purpose: fuzz/regression test for saving and loading blobs with varied caller-provided buffer sizes.

Important APIs/tests: `FuzzSaveLoadBlob` fuzzes `blob []byte` and `buflen uint`, bounds buffer length to 64 MiB, hashes the blob, saves it through `WithBlobUploader`, then loads it into a buffer of fuzzed capacity and verifies the hash.

Control flow and state: each fuzz case creates a repository v2 test repo, saves one data blob, then loads it by handle. Oversized fuzz buffers are skipped to avoid allocator-focused tests.

Dependencies and integration points: exercises repository uploader, packer, index, crypto, and load paths. It references regression issue behavior around caller buffer sizes.

Risks and test signals: strong edge-case signal for buffer reuse and blob round trips, but expensive because each fuzz case creates a repo. It validates hash equality rather than byte-for-byte equality, which is sufficient for SHA-256 collision assumptions.
