# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/KeyBackedRangeMap.h

## Purpose
Provides a database-backed typed range map abstraction built on `KeyBackedMap`, plus an immutable local snapshot representation for efficient range lookups. It lets code store sparse range boundary records in FDB and interpret uncovered regions as a default value.

## Important APIs, Types, And Functions
`KeyRangeMapSnapshot<KeyType, ValueType>` is a reference-counted map of boundary keys to values. It exposes `RangeIter`, `Ranges`, `rangeContaining()`, `intersectingRanges()`, and `ranges()`. `KeyBackedRangeMap` wraps `KeyBackedMap<KeyType, ValueType>` and exposes `getRangeForKey()`, `updateRange()`, and `getSnapshot()`. `ValueType` must support `apply()` for incremental updates and equality for coalescing adjacent ranges.

## Control Flow
`getRangeForKey()` concurrently seeks the boundary at or before a key and the next boundary after it; both must exist to return a concrete range. `updateRangeActor()` reads from the last boundary before `begin` through the first boundary after `end`, applies or replaces values over affected boundaries, inserts missing begin/end boundaries as needed, and erases boundaries whose effective value matches the previous range. It paginates with `GetRangeLimits`, using tiny reads under `buggify()` to stress pagination. `getSnapshotActor()` reads all boundaries covering a requested interval and inserts synthetic begin/end default boundaries if the database map lacks them.

## State And Persistence Behavior
Persistent state is stored under the `KeyBackedMap` prefix as typed boundary keys with encoded `ValueType` values. Uncovered ranges are interpreted as `ValueType()`. `updateRange()` mutates only boundary records and coalesces adjacent equal values to keep storage sparse. Snapshots are in-memory, reference-counted, and intended to be immutable after creation.

## Dependencies And Integration Points
The header depends on `KeyBackedTypes.h`, Flow coroutines, FastRef, typed tuple codecs, transaction creators, and FDB range reads/writes. It integrates with system metadata that needs range-to-property maps, watchable triggers inherited through `KeyBackedMap`, and transaction retry helpers.

## Risks And Test Signals
Risks include off-by-one boundary handling, empty/invalid range updates, relying on read-your-writes when the code explicitly supports non-RYW transactions, incorrect end restoration, and snapshot queries outside the initialized coverage. Test signals should include replace vs apply updates, coalescing adjacent equal values, missing begin/end boundaries, paginated reads, default-value gaps, transaction creator mode, and local snapshot lookup assertions.
