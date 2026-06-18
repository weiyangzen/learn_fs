# sources/storage-engines/rocksdb/db/file_indexer.cc

## Purpose
`file_indexer.cc` implements `FileIndexer`, a precomputed hint structure used by `Version::Get()`-style searches to narrow the file-index range that must be binary-searched in the next level. It reuses comparisons between a target key and the current upper-level file's smallest/largest keys to skip lower-level files that cannot contain the key.

## Important APIs, Types, and Functions
The implemented methods are `FileIndexer::FileIndexer`, `NumLevelIndex`, `LevelIndexSize`, `GetNextLevelIndex`, `UpdateIndex`, `CalculateLB`, and `CalculateRB`. `UpdateIndex` consumes `std::vector<FileMetaData*>* files`, the number of levels, and an `Arena` for persistent allocation. It uses `Comparator::CompareWithoutTimestamp` against `FileMetaData::smallest.user_key()` and `largest.user_key()` to fill `IndexUnit` fields declared in the header.

## Control Flow
`UpdateIndex` is called after a version's file tree is known. It initializes `num_levels_`, allocates `level_rb_`, records each level's rightmost file index, and for levels `1` through `num_levels - 2` allocates an `IndexUnit` array when the upper level is non-empty. Four scans then populate lower-bound and right-bound hints: upper smallest versus lower largest, upper largest versus lower largest, upper smallest versus lower smallest, and upper largest versus lower smallest.

`CalculateLB` scans upper and lower files from left to right. When lower files are definitely smaller, it advances `lower_idx`; otherwise it records the first lower index that may still contain a key greater than the relevant upper key. If lower files are exhausted, remaining upper files receive `lower_size`, an empty interval marker beyond the last lower file. `CalculateRB` mirrors this from right to left, recording the last lower index that may contain a key smaller than the relevant upper key and using `-1` when all lower files are too large.

`GetNextLevelIndex` receives comparison outcomes from the caller: target key versus current file's smallest and largest. For the last level it returns an empty hint interval `[0, -1]`. Otherwise it chooses among the precomputed fields to return candidate lower-level bounds. If the key is below the current smallest, it may reuse the previous upper file's `largest_lb` for the left bound and `smallest_rb` for the right bound. If the key is inside the current file range, it uses smallest/largest combinations. If the key is above the current largest, it uses `largest_lb` and the next level's rightmost file.

## State and Persistence Behavior
All state is in-memory and version-scoped. `next_level_index_` stores one `IndexLevel` per level, each pointing to arena-allocated `IndexUnit` arrays; `level_rb_` is also arena allocated. The class does not own or persist `FileMetaData`; it assumes the file arrays and comparator ordering remain stable for the life of the owning version. There is no disk format impact.

## Dependencies and Integration Points
`FileIndexer` depends on `db/version_edit.h` for `FileMetaData`, `rocksdb/comparator.h`, `memory/arena.h`, and `util/autovector`. It is part of the version/file-search path and integrates with the LSM invariant that non-L0 levels are sorted by non-overlapping key ranges. Timestamp-aware comparators are handled through `CompareWithoutTimestamp`, so the index is based on user-key range overlap rather than timestamp suffixes.

## Risks
The implementation assumes sorted file metadata per level and valid non-overlapping lower-level ranges. Incorrect ordering or comparator mismatch would produce unsafe bounds and missed reads. The bounds use `int32_t`; very large file counts must not exceed `kLevelMaxIndex`. `UpdateIndex` asserts `level_rb_ == nullptr`, so it is not a reusable mutating builder. Empty lower levels intentionally produce intervals such as `[0, -1]` or `[lower_size, lower_size - 1]`, and callers must treat `left > right` as no candidate files.

## Test Signals
`file_indexer_test.cc` directly verifies empty DBs, upper files entirely left or right of lower files, an empty middle level, and mixed overlaps. Assertions exercise all comparison cases passed to `GetNextLevelIndex`: less than smallest, equal smallest, between smallest/largest, equal largest, and greater than largest. Broader signal is indirect through DB point lookup correctness and performance in version searches.
