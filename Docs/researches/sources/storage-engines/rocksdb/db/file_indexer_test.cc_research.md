# sources/storage-engines/rocksdb/db/file_indexer_test.cc

## Purpose
`file_indexer_test.cc` unit-tests `FileIndexer` with deterministic integer key ranges. It verifies that precomputed lower-level search bounds are correct for empty state, non-overlap on either side, empty intermediate levels, and mixed overlap patterns.

## Important APIs, Types, and Functions
`IntComparator` implements `Comparator` over 8-byte integer slices. `FileIndexerTest` owns a four-level `std::vector<FileMetaData*>` array, helper `AddFile`, helper `IntKey`, cleanup through `ClearFiles`, and a wrapper for `FileIndexer::GetNextLevelIndex` that resets output sentinels. Tests are `Empty`, `no_overlap_left`, `no_overlap_right`, `empty_L2`, and `mixed`.

## Control Flow
Each non-empty test allocates an `Arena`, creates a `FileIndexer`, adds synthetic file ranges to levels 1 through 3, calls `UpdateIndex`, and then invokes `GetNextLevelIndex` with representative comparison outcomes. The tests check exact left/right bounds for each current file. The comparison arguments model whether a target key is below the file's smallest key, equal to the smallest key, inside the range, equal to largest, or above largest.

`no_overlap_left` verifies upper-level files that all sit left of next-level files, producing empty right bounds until the target is greater than the upper largest. `no_overlap_right` verifies the inverse, where lower files can be skipped on the left and empty intervals appear as `left == lower_size`, `right == lower_size - 1`. `empty_L2` confirms an empty next level produces `[0, -1]`. `mixed` checks exact overlapping windows across L1-to-L2 and L2-to-L3.

## State and Persistence Behavior
The test manually allocates `FileMetaData` and deletes it after each case. `FileIndexer` allocations use a stack `Arena`, matching production lifetime style. There is no persistence; the test validates in-memory derived indexes over metadata.

## Dependencies and Integration Points
The test includes `db/file_indexer.h`, `db/dbformat.h`, `db/version_edit.h`, RocksDB comparator APIs, stack trace installation, and the RocksDB test harness. It provides direct coverage for the file-indexer component used by version lookup.

## Risks
The comparator uses `reinterpret_cast<const int64_t*>` and asserts 8-byte keys, which is acceptable for this controlled test but not a general key encoding. The synthetic ranges assume sorted files; the tests do not cover unsorted metadata because production should not provide it. The assertions are brittle by design: a small change in bound semantics will surface immediately.

## Test Signals
The exact `ASSERT_EQ` matrices are the primary signal. They cover both valid non-empty intervals and empty intervals where `left > right`, and they check that `LevelIndexSize` returns zero before indexing. A failure here indicates either unsafe file skipping or lost optimization precision in `FileIndexer`.
