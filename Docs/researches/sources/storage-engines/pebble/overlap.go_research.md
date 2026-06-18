# sources/storage-engines/pebble/overlap.go

## Purpose

`overlap.go` adapts Pebble's DB/version/table iterator machinery to the internal `overlap` package. It defines `overlapChecker`, a thin implementation of `overlap.IteratorFactory`, and uses it to determine whether a requested user-key bound overlaps point keys, range deletions, or range keys in an LSM version.

## Important APIs, Types, and Functions

- `overlapChecker` holds the comparer, table iterator factory, iterator options, target `manifest.Version`, object-storage provider, and a `skipRemoteProbe` flag.
- `(*overlapChecker).DetermineLSMOverlap(ctx, bounds)` constructs an `overlap.Checker` with the user-key comparator and itself as iterator factory, optionally installs a remote-table skip predicate, and calls `LSMOverlap`.
- `var _ overlap.IteratorFactory = (*overlapChecker)(nil)` is a compile-time interface assertion.
- `Points(ctx, m)` opens point-key iterators for a table using `newIters(..., iterPointKeys)` and returns `iters.point`.
- `RangeDels(ctx, m)` opens range-deletion iterators using `iterRangeDeletions` and returns `iters.rangeDeletion`.
- `RangeKeys(ctx, m)` opens range-key iterators using `iterRangeKeys` and returns `iters.rangeKey`.

## Control Flow and State

The type is stateful only by holding references needed to open table iterators and inspect the current version. `DetermineLSMOverlap` delegates the actual overlap algorithm to `internal/overlap`. If `skipRemoteProbe` is set, it assigns `checker.SkipProbe` to return true for tables whose backing file is not local according to `objstorage.IsLocalTable`. Local tables are still probed normally.

The iterator methods all use the same pattern: call the `tableNewIters` function with context, table metadata, the checker's `IterOptions`, default `internalIterOpts`, and a specific key-kind selector. Errors propagate immediately. Successful calls return only the iterator type requested by the `overlap.IteratorFactory` interface.

## Persistence and State Behavior

This file does not persist state. It reads existing LSM metadata from `manifest.Version` and opens table iterators through the configured object provider. Its behavior depends on current table locality when `skipRemoteProbe` is active, meaning overlap results may conservatively avoid probing remote-backed tables while still using metadata-level overlap logic provided by the checker.

## Dependencies and Integration Points

Dependencies include `context`, `internal/base` for comparers, bounds, and internal iterators; `internal/keyspan` for range deletion/key iterators; `internal/manifest` for table metadata and versions; `internal/overlap` for the main overlap algorithm; and `objstorage` for local-vs-remote table detection. The code integrates with Pebble table opening through `tableNewIters`, `internalIterOpts`, and iterator-kind constants.

Likely callers are DB code paths that need to determine whether a key span overlaps existing LSM contents before choosing an operation strategy, for example ingestion/excise/delete-only compaction checks or remote-object-aware probing.

## Risks and Edge Cases

- Iterator resource ownership is delegated to the `overlap` checker. Any future change must preserve correct closing semantics in the caller/algorithm.
- `skipRemoteProbe` can change overlap precision for remote-backed tables. It must only be used by callers that can tolerate skipped probing and rely on conservative metadata behavior.
- Passing the wrong `iterPointKeys`, `iterRangeDeletions`, or `iterRangeKeys` selector would silently produce incomplete overlap checks.
- `IterOptions` bounds and filters may affect opened iterators; callers must provide options compatible with the bounds they ask the overlap checker to evaluate.

## Test Signals

There are no tests in this file. Coverage is expected through higher-level tests for operations that call overlap detection. Useful targeted tests would mock table metadata with local and remote backings, assert `SkipProbe` behavior, and verify that point, range deletion, and range key overlaps each request the correct iterator kind.
