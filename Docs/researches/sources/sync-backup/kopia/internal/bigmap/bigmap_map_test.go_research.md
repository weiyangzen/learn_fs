## sources/sync-backup/kopia/internal/bigmap/bigmap_map_test.go

Purpose: external-package tests and benchmarks for exported `bigmap.Map`.

Important APIs/types/functions: `TestGrowingMap`, `BenchmarkMap_NoValue`, `BenchmarkMap_WithValue`, `benchmarkMap`, and local `sha256Key`.

Control flow, state, and persistence: inserts 20,000 SHA-256 keys with deterministic values using small segment/table options to force growth, validates contains/get during insertion, and benchmarks insertion plus repeated lookup.

Dependencies and integration points: uses only exported `bigmap` API, making it a good package-boundary test.

Risks and test signals: validates encryption/decryption under growth. Does not test tampered ciphertext or random-key initialization failures.
