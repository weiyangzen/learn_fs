# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/AsyncIterator.java

## Purpose
`AsyncIterator` extends Java `Iterator` with non-blocking readiness and cancellation for FoundationDB asynchronous result streams.

## Important APIs, Types, And Functions
`onHasNext()` returns a `CompletableFuture<Boolean>` indicating whether `next` can produce another element. `hasNext` remains the blocking form. `next` returns the next element and may block if readiness was not awaited. `cancel` stops outstanding asynchronous work.

## Control Flow
Range iterators implement `onHasNext` around chunk fetch futures. Utility wrappers in `AsyncUtil` delegate readiness, next, remove, and cancel to underlying iterators.

## State And Persistence Behavior
The interface stores no state. Implementations usually keep cursor state and outstanding futures.

## Dependencies And Integration Points
It is central to `RangeQuery`, `MappedRangeQuery`, `LocalityUtil.BoundaryIterator`, `AsyncUtil`, and `CloseableAsyncIterator`.

## Risks And Edge Cases
Calling `next` without awaiting readiness can block. Cancellation semantics depend on implementation and may affect all consumers of shared work.

## Test Signals
Tests should cover readiness futures, blocking `hasNext`, `next` after exhaustion, cancellation, remove delegation, and exception propagation.
