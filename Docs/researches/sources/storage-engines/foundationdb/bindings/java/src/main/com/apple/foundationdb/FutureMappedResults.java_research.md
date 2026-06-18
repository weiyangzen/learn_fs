# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureMappedResults.java

## Purpose
`FutureMappedResults` represents a ready native mapped-range query chunk. Unlike scalar futures, it completes to a lightweight `MappedRangeResultInfo` and defers actual result marshaling until the iterator requests the chunk.

## Important APIs, Types, And Functions
It extends `NativeFuture<MappedRangeResultInfo>`, stores direct-buffer enablement and optional instrumentation, overrides `postMarshal` to avoid automatic close, checks native error through `Future_getError`, and exposes `getResults()` for array or direct-buffer marshaling.

## Control Flow
Native readiness completes the Java future with `MappedRangeResultInfo(this)` but leaves the native future open. `MappedRangeQuery.FetchComplete` calls `data.get()`, which calls `getResults`; that borrows a direct buffer when enabled, fills it through JNI, builds a `MappedRangeResult`, and later closes the native future in the fetch completion finally block.

## State And Persistence Behavior
The native future pointer remains live after readiness until the owning range iterator closes it. Direct buffers are borrowed transiently and returned by the direct iterator.

## Dependencies And Integration Points
It integrates with `MappedRangeQuery`, `MappedRangeResultInfo`, `MappedRangeResult`, `MappedRangeResultDirectBufferIterator`, `DirectBufferPool`, and `EventKeeper`.

## Risks And Edge Cases
Forgetting to close the future after consuming results leaks native memory. Direct-buffer format must match `MappedRangeResultDirectBufferIterator`. Instrumentation counts hit/miss and JNI calls before marshaling.

## Test Signals
Tests should cover direct-buffer hit and miss paths, native error before marshaling, deferred close semantics, empty/multi-row mapped chunks, and cancellation from iterator cancel.
