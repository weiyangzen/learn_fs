# sources/storage-engines/pebble/internal/keyspan/keyspanimpl/level_iter.go

## Purpose
Implements `LevelIter`, a `FragmentIterator` over spans stored in the sstables of one non-overlapping level or L0 sublevel.

## Important APIs, Types, And Functions
`TableNewSpanIter` opens a per-table span iterator. `LevelIter` stores comparer, key type, manifest layer, table iterator factory, file iterator, cached per-file iterator, wrapper function, and reusable straddle span. `NewLevelIter`, `Init`, all positioning methods, `SetContext`, `Close`, `WrapChildren`, and `TreeStepsNode` are the public surface.

## Control Flow
Absolute seeks use manifest `LevelIterator.SeekGE`/`SeekLT` to find candidate files, optionally return empty straddling spans between range-key file bounds, then open/reuse a file iterator and seek within it. Relative movement first advances within the current file, then `moveToNextFile` or `moveToPrevFile` scans files until a span is found, emitting straddle spans for gaps when enabled.

## State And Persistence Behavior
The iterator opens at most one per-file span iterator at a time and caches the last opened iterator when staying on the same file. It closes the cached iterator on file changes or `Close`. It does not persist data; it reads file metadata and delegates table access to `newIter`.

## Dependencies And Integration Points
Depends on `manifest.TableMetadata`, `manifest.LevelIterator`, `manifest.KeyType`, `base.Compare`, `keyspan.FragmentIterator`, assertions, and `treesteps`. It integrates range deletions (`KeyTypePoint`) and range keys (`KeyTypeRange`) into higher-level merging iterators.

## Risks And Edge Cases
Risks include stale file iterator reuse, incorrect sentinel positioning before/after nil files, inconsistent straddle-span behavior at edges, and differences between point-key and range-key bounds. Straddle spans currently apply only to range keys.

## Test Signals
`level_iter_test.go` checks datadriven file traversal and equivalence between merging per-file iterators directly and merging through `LevelIter`, ignoring expected empty straddling spans.
