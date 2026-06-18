## sources/sync-backup/restic/internal/repository/index/testing.go

Purpose: test helper for finalizing and merging a `MasterIndex`.

Important APIs: `TestMergeIndex(t, mi)` finalizes non-final indexes, assigns random IDs, calls `MergeFinalIndexes`, and returns the finalized indexes, remaining index count, and assigned ID set.

Control flow and state: mutates the provided master index by finalizing pending indexes and merging them. It uses random IDs to simulate saved index IDs without backend I/O.

Dependencies and integration points: used by master index tests and benchmarks. Depends on restic random IDs and test assertions.

Risks and test signals: helper is for tests only; it bypasses actual `SaveIndex`, so persistence errors are covered elsewhere.
