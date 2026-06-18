# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureResults.java

## Purpose
`FutureResults` represents a native range-query result chunk and defers expensive result marshaling until `RangeQuery` consumes the ready chunk.

## Important APIs, Types, And Functions
It extends `NativeFuture<RangeResultInfo>`, stores direct-buffer enablement and optional instrumentation, returns `RangeResultInfo(this)` after checking `Future_getError`, overrides `postMarshal` to avoid automatic close, and exposes `getResults()` for either `FutureResults_get` or `FutureResults_getDirect`.

## Control Flow
`FDBTransaction.getRange_internal` creates it. Readiness completes the Java future without disposing native memory. `RangeQuery.FetchComplete` calls `RangeResultInfo.get`, which marshals the current chunk, updates iterator state, then closes the future in a finally block.

## State And Persistence Behavior
Native memory stays live between readiness and chunk consumption. Direct buffers are borrowed per marshaling attempt and returned after constructing `RangeResult`.

## Dependencies And Integration Points
It connects `FDBTransaction`, `RangeQuery`, `RangeResultInfo`, `RangeResult`, `RangeResultDirectBufferIterator`, `DirectBufferPool`, and `EventKeeper`.

## Risks And Edge Cases
If iterator code fails to close a `FutureResults`, native memory can leak. Direct-buffer capacity must handle at least one maximum-size key/value pair. Errors are checked before result extraction, not by automatic base close.

## Test Signals
Tests should cover array and direct-buffer marshaling, empty chunks, `more` flag propagation, future close after consumption, hit/miss metrics, and native error propagation.
