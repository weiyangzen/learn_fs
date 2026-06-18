# sources/storage-engines/pebble/internal/manifest/version.go

## Purpose
`version.go` defines a Pebble manifest `Version`: the complete in-memory set of tables and blob files visible in the LSM. It also implements version lists, ordering checks, overlap queries, range-key-set region tracking, reference release, and in-use key range calculation.

## Important APIs, Types, And Functions
- `Version` contains `Levels`, `L0SublevelFiles`, `RangeKeyLevels`, `BlobFiles`, `MarkedForCompaction`, `RangeKeySetRegions`, refcount/list links, and a comparer.
- Constructors include `NewInitialVersion`, `NewVersionWithFiles`, and `NewVersionForTesting`.
- Formatting/parsing includes `String`, `DebugString`, `DebugStringFormatKey`, `ParseVersionDebug`, and `describeSublevels`.
- Query and iteration APIs include `KeyRange`, `ExtendKeyRange`, `SortBySmallest`, `Contains`, `Overlaps`, `HasOverlap`, `AllLevelsAndSublevels`, and `AllTables`.
- Lifetime APIs include `Ref`, `Unref`, `UnrefLocked`, `unrefFiles`, `ObsoleteFiles`, and `VersionList`.
- `CalculateInuseKeyRanges`, `seekGT`, `CheckOrdering`, and blob invariant validation implement core correctness logic.

## Control Flow
Constructors build per-level B-trees and range-key subsets, populate range-key-set region trees, and initialize L0 organizer state. Overlap logic uses iterative expansion for whole L0 because L0 files can overlap transitively; L1+ uses key-sorted level slices. `CalculateInuseKeyRanges` descends levels, merging existing accumulated ranges with overlapping files and skipping files contained within already accumulated ranges. `CheckOrdering` applies relaxed legacy checks for whole L0 and strict sorted non-overlap checks for L1+ and L0 sublevels.

## State And Persistence Behavior
`Version` is the in-memory result of manifest replay and subsequent version edits. Reference counts keep table backings and blob files alive until no referenced version needs them. `RangeKeyLevels` and `RangeKeySetRegions` duplicate derived state for fast range-key queries. `L0SublevelFiles` must be populated by `L0Organizer` after `BulkVersionEdit.Apply`.

## Dependencies And Integration Points
The file integrates with level metadata, table metadata, blob metadata, virtual backing lifetime, L0 organizer, region trees, version edits, compaction picking, scan cursors, and event/debug tooling. It depends on `base`, `axisds/regiontree`, `strparse`, and Go `iter`/`slices` helpers.

## Risks And Test Signals
Major risks include L0 overlap expansion, range-key-only handling, version refcount release, blob file invariant drift, and ordering compatibility with older RocksDB/Pebble manifests. `version_test.go` covers key range union, overlaps, contains, unref/list removal, ordering datadriven cases, deterministic and randomized in-use range calculation, and zero-allocation iteration.
