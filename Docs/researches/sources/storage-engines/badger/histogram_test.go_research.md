# sources/storage-engines/badger/histogram_test.go

## Purpose
`histogram_test.go` verifies the internal histogram builder for key and value sizes.

## Important APIs, Types, and Functions
- `TestBuildKeyValueSizeHistogram`: two subtests for uniform one-byte entries and mixed one/two/three-byte entries.

## Control Flow and State
Each subtest uses `runBadgerTest`, writes entries in a single update transaction, calls `db.buildHistogram(nil)`, and validates both key and value histogram fields.

## Persistence Behavior
The tests use normal Badger writes in a temporary directory but inspect the in-memory histogram result, not persisted histogram state.

## Dependencies and Integration Points
Depends on `runBadgerTest`, `DB.Update`, `NewEntry`, and `testify/require`.

## Risks and Edge Cases
The tests do not cover prefix-restricted histograms, empty databases, large values, overflow bins, or printed output formatting.

## Test Signals
Good focused signal for binning and aggregate math on small keys/values. It also indirectly exercises iterator-based size collection.
