## sources/sync-backup/restic/internal/repository/index/associated_data_test.go

Purpose: tests `AssociatedSet` behavior for stable-index entries, overflow entries, and set algebra.

Important helpers/tests: `noopSaver` saves index bytes by hash. `makeFakePackedBlob` creates a blob handle and packed blob. `list` collects keys. `TestAssociatedSet` covers insert, set, update, delete, overflow handling, and `String`. `TestAssociatedSetWithExtendedIndex` verifies sets created before later master-index extension use overflow for new blobs. `TestAssociatedSetIntersectAndSub` verifies value preservation and membership for intersections and differences.

Control flow and state: tests build a `MasterIndex`, store packs, flush to finalize, and then construct associated sets. Overflow map size is asserted directly.

Dependencies and integration points: validates the stable offset contract between `AssociatedSet` and `MasterIndex`.

Risks and test signals: tests use synthetic blobs and no real repository persistence, so they focus on data-structure behavior rather than integration with prune/check commands.
