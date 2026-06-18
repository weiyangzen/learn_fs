# sources/storage-engines/rocksdb/db/file_indexer.h

## Purpose
`file_indexer.h` declares the `FileIndexer` class and documents the search-hint model used to speed lower-level file lookup. The key idea is that comparisons already made against an upper-level file can be translated into a narrower candidate interval in the next level, avoiding repeated full binary searches across increasingly large lower levels.

## Important APIs, Types, and Functions
The public API is `FileIndexer(const Comparator*)`, `NumLevelIndex`, `LevelIndexSize`, `GetNextLevelIndex`, and `UpdateIndex`. `kLevelMaxIndex` records the maximum supported index value. Private types are `IndexUnit`, which stores four precomputed hints (`smallest_lb`, `largest_lb`, `smallest_rb`, `largest_rb`), and `IndexLevel`, which stores an array of `IndexUnit` entries for one level.

The private helpers `CalculateLB` and `CalculateRB` are declared with comparator and setter callbacks so the implementation can reuse the same scan logic for smallest/largest combinations.

## Control Flow
Clients build the index with the complete per-level `FileMetaData` vectors. During lookup, a caller compares a key with the current file's smallest and largest user keys, passes the comparison results to `GetNextLevelIndex`, and receives left/right bounds for the next-level search. Header comments enumerate the three major comparison outcomes: key below the current file, key inside its range, and key above its range.

## State and Persistence Behavior
`FileIndexer` stores `num_levels_`, a non-owning `Comparator` pointer, `next_level_index_`, and `level_rb_`. It uses arena allocation, so lifetime is tied to the arena supplied to `UpdateIndex`, typically the owning version's arena. It is a derived in-memory structure and is not serialized.

## Dependencies and Integration Points
The declaration depends on `Comparator`, `FileMetaData`, `Arena`, `autovector`, and standard functional/vector types. It sits between version metadata construction and the read path. It is designed for the sorted levels below L0, which is why `GetNextLevelIndex` asserts `level > 0`; L0 overlap semantics are different.

## Risks
The header exposes a low-level API that relies on callers passing comparison signs consistent with the same comparator used at build time. Bounds are signed `int32_t` values where `right_bound == -1` and `left_bound == right_bound + 1` are valid empty ranges. Misinterpreting those sentinels can cause invalid array access or missed files. Since arrays are arena-backed and there is no destructor cleanup, the arena lifetime contract is critical.

## Test Signals
The focused test file checks `LevelIndexSize`, empty input behavior, and expected next-level ranges for synthetic integer-key levels. Production signal comes from point lookups and compaction/version metadata tests that would fail if file search skipped candidate SSTs.
