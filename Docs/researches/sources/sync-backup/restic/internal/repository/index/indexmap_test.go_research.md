## sources/sync-backup/restic/internal/repository/index/indexmap_test.go

Purpose: tests and benchmark for the custom `indexMap` and `hashedArrayTree`.

Important tests: `TestIndexMapBasic` inserts 400 random IDs and verifies retrieval/counts. `TestIndexMapForeach` checks empty iteration, values, and early break. `TestIndexMapForeachWithID` verifies duplicate keys with noise entries. `TestHashedArrayTree` checks allocation/ref stability. `BenchmarkIndexMapHash` measures maphash use over random IDs. `TestIndexMapFirstIndex` and `TestIndexMapFirstIndexDuplicates` verify stable first-index behavior.

Control flow and state: tests use deterministic random seeds and package-internal access to unexported structures.

Dependencies and integration points: protects the memory-efficient structure that backs all index lookup behavior and the associated data offset contract.

Risks and test signals: tests cover functional invariants but not 32-bit bloom-filter fallback or extremely large overflow limits.
