## sources/sync-backup/restic/internal/repository/index/index_internal_test.go

Purpose: internal test for `Oversized` threshold logic.

Important tests: `TestIndexOversized` creates an index just below `indexMaxBlobs + pack.MaxHeaderEntries`, asserts not oversized, adds one more blob, and asserts oversized.

Control flow and state: test bypasses public `StorePack` after adding one pack ID and calls `idx.store` directly to create many entries quickly.

Dependencies and integration points: protects rewrite/splitting logic in `MasterIndex.Rewrite`, which uses `Oversized` to decide whether a full index should be rewritten.

Risks and test signals: focused threshold coverage; it does not test serialization or real rewrite behavior, which is covered in master index tests.
