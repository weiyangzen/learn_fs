# sources/storage-engines/pebble/internal/manifest/annotator_table.go

## Purpose
This file provides cached aggregate computations over `TableMetadata` B-trees, including whole-level, multi-level, range-limited, and version-wide annotations. It is used for efficient manifest-derived decisions such as counting overlapping files or picking a best candidate file without scanning every table.

## Important APIs, Types, And Functions
`TableAnnotator[T]` embeds `annotator[T, *TableMetadata]` and adds an optional `partialOverlapFunc`. `MakeTableAnnotator` constructs one from `TableAnnotatorFuncs`. `NewTableAnnotationIdx` allocates cache slots. `accumulateRangeAnnotation` is the core range traversal. Public APIs include `LevelAnnotation`, `MultiLevelAnnotation`, `LevelRangeAnnotation`, and `VersionRangeAnnotation`. `MakePickFileAnnotator` specializes a table annotator that returns one preferred eligible file using `PickFileAnnotatorFuncs`.

## Control Flow
Whole-level annotation delegates to `nodeAnnotation`. Range annotation descends the B-tree, using key comparisons to find item and child ranges that overlap the requested `UserKeyBounds`. If a subtree is known fully inside both bounds, it reuses the cached node annotation. Boundary files can use `PartialOverlap` when only part of the file overlaps; otherwise the normal item annotation is merged. Version range annotation iterates L0 sublevel slices and levels 1+, accumulating per-slice range annotations.

## State, Persistence, And Side Effects
The file maintains a package-global `nextTableAnnotationIdx` used at initialization time. Computed annotations are transient node caches and are invalidated by B-tree mutation. No values are persisted. The API assumes caller-provided callbacks are pure relative to their cacheability flag.

## Dependencies And Integration Points
Dependencies include `sort`, CockroachDB `errors`, and Pebble `base` key bounds/comparers. Integration points include `LevelMetadata`, `LevelSlice`, `Version.L0SublevelFiles`, the copy-on-write B-tree, and compaction/manifest code that needs fast aggregate metadata.

## Risks And Edge Cases
The range traversal is sensitive to inclusive/exclusive bound semantics and to B-tree ordering. Only boundary files can use `PartialOverlap`; a missing partial callback means boundary files are counted as whole files. Index reuse or over-allocation can corrupt cache lookup or panic. Version-wide annotation must handle L0 sublevels separately because L0 is not represented as a single non-overlapping level.

## Test Signals
`annotator_test.go` validates count annotations over whole levels and ranges, including empty ranges, random bounds, and performance comparisons against `Version.Overlaps`. It also tests `MakePickFileAnnotator` by ensuring the smallest eligible file remains selected across insertions.
