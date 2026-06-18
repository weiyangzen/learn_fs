# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeResultInfo.java

## Purpose
`MappedRangeResultInfo` is a lightweight readiness token that defers mapped range result marshaling to its owning `FutureMappedResults`.

## Important APIs, Types, And Functions
The constructor stores a `FutureMappedResults`; `get()` calls `f.getResults()`.

## Control Flow
`FutureMappedResults.getIfDone_internal` creates this object after native error checking. `MappedRangeQuery.FetchComplete` calls `get` when it is ready to consume the chunk.

## State And Persistence Behavior
It stores only a reference to the native future wrapper. It does not own resources directly, but its reference keeps the future reachable until consumed.

## Dependencies And Integration Points
It integrates `FutureMappedResults` and `MappedRangeQuery`.

## Risks And Edge Cases
Calling `get` after the underlying future is closed will fail. Repeated `get` calls may attempt repeated native marshaling from the same native future and should not be assumed safe.

## Test Signals
Tests should verify deferred `get` calls, close-after-consumption behavior, and failure after underlying future closure.
