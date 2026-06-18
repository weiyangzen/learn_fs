# sources/storage-engines/pebble/internal/manifest/version_test.go

## Purpose
This test file validates version-level queries, ordering checks, reference-list behavior, in-use key range calculation, and allocation behavior for table iteration.

## Important APIs And Tests
- `TestIkeyRange` checks `KeyRange` union behavior.
- `TestOverlaps` datadriven-tests `Version.Overlaps` with inclusive/exclusive bounds.
- `TestContains` validates exact file membership for overlapping L0 and non-overlapping L1.
- `TestVersionUnref` verifies last unref removes a version from `VersionList`.
- `TestCheckOrdering` runs datadriven ordering validation fixtures.
- `TestCalculateInuseKeyRanges` covers deterministic multi-level range merging cases.
- `TestCalculateInuseKeyRangesRandomized` checks generated non-overlapping levels over many random spans.
- `TestIterAllocs` asserts `LevelSlice.All` and `LevelMetadata.All` perform zero allocations.

## Control Flow
Tests construct versions from either explicit `TableMetadata` instances or debug strings, initialize L0 organizers, invoke version APIs, and compare returned slices/booleans/debug output. The randomized in-use test builds non-overlapping files per level and asserts every overlapping file span is contained within some calculated range.

## State And Persistence Behavior
Most tests use in-memory versions, but debug parsing mirrors manifest debug output. Reference tests cover version-list state and deletion callback flow.

## Dependencies And Integration Points
The tests depend on `NewVersionForTesting`, `ParseVersionDebug`, `L0Organizer`, `LevelMetadata`, `TableMetadata`, `base`, `testkeys`, datadriven fixtures, and `testing.AllocsPerRun`.

## Risks And Test Signals
Coverage is strong for overlaps, range merging, and ordering. Randomized tests log seeds to reproduce failures. The allocation test guards performance-sensitive iterator APIs used heavily by compaction and query planning.
