# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/KeyRangeMap.h

## Purpose
Provides in-memory and database-backed key range map utilities for FoundationDB keyspace metadata. It wraps the generic `RangeMap` with FDB `Key`/`KeyRangeRef` types, adds coalescing insertion behavior, tracks actors over key ranges, and declares `krm*` helpers for range maps persisted in the database.

## Important APIs, Types, And Functions
`KeyRangeMap` inherits `RangeMap<Key, Val, KeyRangeRef>` and exposes `insert()`, `modify()`, raw erase/insert helpers, and `getAffectedRangesAfterInsertion()`. `CoalescedKeyRangeMap` and `CoalescedKeyRefRangeMap` coalesce adjacent equal values for owned `Key` and borrowed `KeyRef` variants. `KeyRangeActorMap` maps ranges to `Future<Void>` actors, supports cancellation, and checks if a live actor covers a key. The declared `krmGetRanges`, `krmGetRangesUnaligned`, `krmSetPreviouslyEmptyRange`, `krmSetRange`, `krmSetRangeCoalescing`, and `krmDecodeRanges` implement persisted range-map access under a prefix.

## Control Flow
In-memory insertions split existing ranges at begin/end and replace covered spans. Coalesced insertions inspect neighboring values, decide whether begin/end boundary records are necessary, erase the covered map interval, then insert only needed boundaries. `modify()` ensures begin and end boundaries exist and returns intersecting ranges for mutation. Persisted `krm*` functions read/align encoded boundary records and set ranges transactionally.

## State And Persistence Behavior
In-memory maps store ordered boundaries and a `mapEnd`. Coalescing reduces redundant adjacent boundaries. `KeyRangeActorMap` stores futures and treats invalid/ready futures as non-live. Persisted range maps store boundary keys and values under an FDB prefix; the header declares but does not implement their transaction behavior.

## Dependencies And Integration Points
The header depends on Flow types, FDB key utilities, Boost ranges, `IndexedSet`, system data, `fdbrpc/RangeMap`, and client knobs for persisted range-map read limits. It integrates with shard maps, server metadata, actor cancellation tracking, and system-key range-map schemas.

## Risks And Test Signals
Risks include boundary off-by-one errors, incorrect use of `keyAfter()` for single-key insertion, borrowed `KeyRef` lifetime in coalesced maps, raw insert/erase bypassing invariants, and persisted map alignment returning too few records if knob limits are too low. Test signals should cover full-keyspace endpoints, empty range insertion, adjacent equal coalescing, single-key insertions, `modify()` boundary creation, actor cancellation, and persisted `krmDecodeRanges` alignment.
