# sources/storage-engines/pebble/internal/keyspan/keyspanimpl/level_iter_test.go

## Purpose
Tests manifest-backed level span iteration and validates `LevelIter` equivalence with direct file iterators.

## Important APIs, Types, And Functions
`TestLevelIterEquivalence` constructs synthetic levels, table metadata, a `BulkVersionEdit`, and compares two `MergingIter`s: one over file iterators and one over `LevelIter`s. `TestLevelIter` parses datadriven file metadata and spans, then runs `NewLevelIter` commands with optional range-delete mode.

## Control Flow
The equivalence test creates file metadata with range-key bounds, applies it to a version, initializes level iterators, then walks both merged views forward, skipping expected empty straddle spans from `LevelIter`. The datadriven test builds `manifest.TableMetadata` per file, opens table iterators by table number, and prints results with `iter.String()` extra info.

## State And Persistence Behavior
All files and versions are synthetic in memory. Per-file span iterators are simple `keyspan.NewIter` instances.

## Dependencies And Integration Points
Depends on `manifest`, `base`, `keyspan`, `datadriven`, `crstrings`, and `require`. It exercises the same manifest metadata APIs used by production level iteration.

## Risks And Edge Cases
The synthetic metadata may omit some real table fields, so it focuses on bounds and ordering rather than table-cache I/O. Equivalence skips empty straddle spans, so dedicated datadriven coverage is needed for those.

## Test Signals
Failures point to wrong file selection, bound filtering, straddle emission, iterator reuse, or mismatch with the simpler direct-merge model.
