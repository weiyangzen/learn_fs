# sources/storage-engines/pebble/internal/manifest/level_metadata_test.go

## Purpose
This test file validates `LevelMetadata`, `LevelSlice`, and `LevelIterator` behavior, especially bounded iteration, seeking, filtering by key type, and finding exact table metadata within levels.

## Important APIs And Helpers
- `TestLevelIterator` uses datadriven commands over `testdata/level_iterator` to define slices and execute iterator commands.
- `TestLevelIteratorFiltered` uses parsed debug table metadata and filters iterators by point/range/both keyspaces.
- `runIterCmd` drives `first`, `last`, `next`, `prev`, `seek-ge`, and `seek-lt`; it randomly cross-checks `PeekNext` against `Next`.
- `makeTestTableMetadata` builds 10,000 non-overlapping tables and key probes for deterministic seek testing.
- `TestLevelIteratorSeek` and `TestLevelIteratorFind` exercise direct seek and exact lookup behavior.

## Control Flow
Datadriven tests parse table definitions, construct key-sorted `LevelSlice`s, optionally reslice them, and run scripted iterator operations. The large seek test alternates probe keys that do and do not exist in table bounds to verify `SeekGE` and `SeekLT` choose the expected adjacent table.

## State And Persistence Behavior
There is no on-disk persistence, but the tests initialize `TableBacking` where needed because level B-trees and release paths rely on refcountable metadata. The datadriven filter tests parse the same debug format used by other manifest tests.

## Dependencies And Integration Points
The tests integrate with `ParseTableMetadataDebug`, `NewLevelSliceKeySorted`, `MakeLevelMetadata`, `bytealloc`, `testkeys`, and datadriven fixtures under `testdata/level_iterator*`.

## Risks And Test Signals
The tests strongly signal correctness for B-tree seek semantics and bounded iterators. Residual risk remains around invariant-only panics and uncommon interleavings of filters with reslicing, but the scripted and large-table coverage catches common iterator regressions.
