# sources/storage-engines/pebble/internal/manifest/annotator_test.go

## Purpose
This file tests the table annotation framework using concrete annotators over synthetic level metadata. It verifies cached whole-level annotation, range annotation, pick-file aggregation, and benchmark behavior.

## Important APIs, Types, And Functions
`NumFilesAnnotator` counts tables by merging `uint64` values. `makeTestVersion` creates a test `Version` with files in level 6, each covering a 10-key span. `TestNumFilesAnnotator`, `TestPickFileAggregator`, `TestNumFilesRangeAnnotationEmptyRanges`, and `TestNumFilesRangeAnnotationRandomized` are the main correctness tests. `BenchmarkNumFilesAnnotator` and `BenchmarkNumFilesRangeAnnotation` measure whole-level and range aggregation costs.

## Control Flow
The tests construct versions, mutate the underlying level B-tree through insertions/deletions, and compare annotator results with expected counts or with `Version.Overlaps`. Randomized range tests use a deterministic PCG seed. The range benchmark alternates deleting and reinserting files to exercise cache invalidation under small mutations.

## State, Persistence, And Side Effects
All state is in-memory test state. The tests directly mutate `v.Levels[6].tree`, so they exercise B-tree annotation invalidation paths. `makeTestVersion` initializes physical table backings to satisfy file metadata ref/unref expectations.

## Dependencies And Integration Points
The file depends on `math/rand/v2`, `testing`, Pebble `base`, and `testify/require`. It integrates annotation APIs with `Version`, `LevelMetadata`, B-tree mutation, user-key bounds, and overlap iteration.

## Risks And Edge Cases
The tests intentionally use annotator index `0`, which is safe in the isolated test process but demonstrates why production annotators must allocate distinct indexes. Empty-range tests delete blocks of files to cover holes and partial overlaps. Random tests cover many bounds but not custom `PartialOverlap` behavior or unstable cacheability.

## Test Signals
Passing tests signal that cached annotations update after tree edits, range pruning matches `Version.Overlaps`, and pick-file aggregation preserves the preferred file. Benchmarks provide performance signals for cached aggregation versus explicit overlap scans.
