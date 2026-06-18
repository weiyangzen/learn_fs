# sources/storage-engines/foundationdb/fdbclient/KeyRangeMap.cpp

## Purpose
`KeyRangeMap.cpp` implements the persistent key-range-map convention used throughout FoundationDB metadata. A map stores transition points under a prefix; helpers read aligned or unaligned ranges, set ranges, set previously empty ranges, coalesce adjacent equal-valued ranges, and identify actor-map ranges affected by insertions.

## Important APIs, Types, And Functions
Key APIs include `KeyRangeActorMap::getRangesAffectedByInsertion()`, `krmDecodeRanges()`, `krmGetRanges()` overloads for `Transaction*` and `ReadYourWritesTransaction`, `krmGetRangesUnaligned()` overloads, `krmSetPreviouslyEmptyRange()` overloads, `krmSetRange()` overloads, and `krmSetRangeCoalescing()` overloads. The private template `krmSetRangeCoalescing_()` contains the coalescing algorithm shared by transaction types.

## Control Flow
Reads form `[mapPrefix + begin, mapPrefix + end)` and fetch one transition at or before begin plus one beyond end. `krmDecodeRanges()` strips prefixes and emits boundary key/value pairs at the requested begin, internal transition points, and requested end unless `more` remains. Unaligned reads include the next key past end so the decoded range may start/end at actual transition points. Basic writes read the old value at range end, add a conflict range, clear prefixed transitions inside the target, set begin to the new value, and set end to the previous value. Coalescing reads adjacent transitions, extends the clear range left/right when values match within `maxRange`, adds conflict ranges for the observed boundaries, clears the combined range, and writes only the necessary begin/end transitions.

## State And Persistence Behavior
Persistent state is encoded as transition keys under caller-provided prefixes. Empty values are valid map values and often represent absence/default. Coalescing maintains the invariant that adjacent ranges should not have identical values except at `maxRange` boundaries. `KeyRangeActorMap` state is in-memory and tracks actor futures by range.

## Dependencies And Integration Points
The file depends on `KeyRangeMap.h`, `NativeAPI.actor.h`, `CommitTransaction`, `FDBTypes`, `ReadYourWrites`, Flow unit tests, transaction conflict APIs, key selectors, and FoundationDB arenas. It is used by bulk load/dump metadata, range locks, shard metadata, and other source-tree components that need compact range-state maps.

## Risks And Edge Cases
The code explicitly warns that multiple `krmSetRangeCoalescing()` calls on the same prefix in one transaction must be awaited sequentially; concurrent calls can observe the same snapshot and corrupt transition invariants. `krmDecodeRanges()` asserts shape assumptions when `kv.more` is true and must preserve arena lifetimes from both source ranges and fetched keys. Boundary math relies on prefix ordering and `keyAfter`/`strinc`. Empty result or too-small limits can produce incomplete maps if callers ignore `more`.

## Test Signals
Local tests cover aligned and unaligned decode behavior with begin/end inside and outside transition points. Broader validation should include coalescing left/right/both, no-op writes, empty-value ranges, ReadYourWrites sequencing, conflict-range behavior, and users such as bulk-load metadata and range locks preserving KRM invariants.
