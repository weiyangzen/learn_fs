# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResultInfo.java

## Purpose
`RangeResultInfo` is a lightweight readiness token for deferred normal range result marshaling.

## Important APIs, Types, And Functions
It stores a `FutureResults` reference and exposes `get()` to call `f.getResults()`.

## Control Flow
`FutureResults.getIfDone_internal` returns this after native error checking. `RangeQuery.FetchComplete` calls `get` when ready to consume the chunk.

## State And Persistence Behavior
It stores only the future reference. Resource ownership remains with `FutureResults`.

## Dependencies And Integration Points
It connects `FutureResults` to `RangeQuery`.

## Risks And Edge Cases
Repeated `get` calls or calls after future close are not safe API contracts. The object is package-private to keep use constrained.

## Test Signals
Tests should cover deferred marshaling, close-after-use, and failure after underlying future closure.
