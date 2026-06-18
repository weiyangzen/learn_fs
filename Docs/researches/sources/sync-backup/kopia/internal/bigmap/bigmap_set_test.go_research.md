## sources/sync-backup/kopia/internal/bigmap/bigmap_set_test.go

Purpose: external-package tests and benchmarks for exported `bigmap.Set`.

Important APIs/types/functions: `TestGrowingSet`, `BenchmarkSet`, and `TestSetPanics`.

Control flow, state, and persistence: inserts deterministic SHA-256 keys, verifies duplicate puts return false, checks previous and not-yet-inserted membership, benchmarks put/contains, and asserts invalid key lengths panic.

Dependencies and integration points: tests the public set API through test logging contexts.

Risks and test signals: confirms growth stability and input validation. Does not test close idempotence or mmap fallback behavior.
