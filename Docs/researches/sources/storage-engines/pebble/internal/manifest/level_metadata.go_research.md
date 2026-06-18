# sources/storage-engines/pebble/internal/manifest/level_metadata.go

## Purpose
`level_metadata.go` implements the in-memory collection, slicing, and iteration model for table metadata within one LSM level. It wraps Pebble's copy-on-write B-tree with aggregate metrics, immutable `LevelSlice` views, and bounded/filterable `LevelIterator`s.

## Important APIs, Types, And Functions
- `LevelMetadata` holds the level number, aggregate table size, aggregate blob reference size, virtual table count/size, and a B-tree of `*TableMetadata`.
- `MakeLevelMetadata`, `insert`, `remove`, `clone`, and `release` construct and mutate the B-tree-backed level state while maintaining aggregate metrics.
- `LevelSlice` is an immutable bounded view over a level, with `All`, `Iter`, `Len`, `Reslice`, `Overlaps`, `HasOverlap`, and size-summing helpers.
- `LevelIterator` provides `First`, `Last`, `Next`, `PeekNext`, `Prev`, `SeekGE`, `SeekLT`, `Current`, `Take`, and `Filter`.
- `KeyType` distinguishes combined, point-only, and range-only table keyspaces.

## Control Flow
Levels are built with sequence-number ordering for whole L0 and smallest-key ordering for L1+ or L0 sublevels. Slices preserve immutable iterator bounds over the underlying B-tree. Seek operations binary-search within key-sorted B-tree nodes, then constrain to slice bounds and skip tables filtered out by key type. `Reslice` passes mutable start/end iterators to a caller and constructs a new inclusive bounded slice from their final positions.

## State And Persistence Behavior
This file owns in-memory state derived from manifests rather than the manifest format itself. Clones preserve copy-on-write B-tree references; `release` decrements table references through the B-tree. Aggregate table size, estimated reference size, and virtual table metrics must remain consistent with B-tree insertions/removals.

## Dependencies And Integration Points
It depends on the manifest B-tree implementation, `TableMetadata` bounds and key-type helpers, `base.UserKeyBounds`, metrics, invariants, and Go iterator sequences. `Version`, `BulkVersionEdit.Apply`, compaction picking, overlap calculation, and scan cursors all use `LevelMetadata` and `LevelIterator`.

## Risks And Test Signals
Important risks include using `SeekGE`/`SeekLT` on a sequence-sorted whole L0 iterator, off-by-one errors from inclusive slice bounds, stale aggregate metrics after edits, and filter logic that misses point-only or range-only tables. `level_metadata_test.go` covers datadriven iteration, filtered iteration, seek correctness over 10k tables, find behavior across levels, and `PeekNext` consistency.
