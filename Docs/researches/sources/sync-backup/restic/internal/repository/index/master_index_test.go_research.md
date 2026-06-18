## sources/sync-backup/restic/internal/repository/index/master_index_test.go

Purpose: broad behavioral and performance coverage for `MasterIndex`.

Important tests/helpers: `TestMasterIndex` covers lookup and size across multiple indexes and duplicate blob IDs. `TestMasterIndexAddPending` and `TestMasterIndexStorePackRemovesPending` cover pending state. `noopSaver` hashes saved index bytes. `TestMasterMergeFinalIndexes` verifies merge and duplicate removal. `createRandomMasterIndex` supports benchmarks for allocation, merge, lookup, iteration, and GC. `createFilledRepo`, `TestIndexSave`, and `TestIndexSavePartial` validate rewrite/save fallback against real repos and checker. `loadIndexAndCollectBlobs`, `collectBlobs`, `TestMasterIndexIncrementalLoad`, and `listPacks` cover incremental reload. `TestRewriteOversizedIndex`, `TestRewriteSplitPacks`, and `TestRewriteFullPacks` cover rewrite splitting, split pack entries, excluded packs, and duplicate full indexes.

Control flow and state: tests use both synthetic `Index` instances and full test repositories. Some tests temporarily replace package variables `index.Full` and `index.Oversized`, restoring them with defer.

Dependencies and integration points: integrates repository, data snapshot creation, checker validation, pack/crypto size helpers, progress counters, and cmp diffs.

Risks and test signals: very strong integration signal for index lifecycle, but some tests are heavier because they create real repositories and snapshots. Replacing global thresholds in tests means parallel execution must be avoided for those cases.
