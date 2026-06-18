# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/AsyncIterable.java

## Purpose
`AsyncIterable` is the FoundationDB binding abstraction for asynchronously iterable result sets such as range queries.

## Important APIs, Types, And Functions
It extends `Iterable<T>` but narrows `iterator()` to return `AsyncIterator<T>`. `asList()` asynchronously materializes all results into a list.

## Control Flow
Implementations return iterators that expose asynchronous readiness through `onHasNext`. `asList` may either optimize the provider-specific operation or delegate to `AsyncUtil.collect`.

## State And Persistence Behavior
The interface stores no state. Implementations may own transactions, native futures, or buffered chunks.

## Dependencies And Integration Points
It is implemented by `RangeQuery`, `MappedRangeQuery`, and wrappers returned by `AsyncUtil.mapIterable`.

## Risks And Edge Cases
Materializing large ranges with `asList` can consume substantial memory. Iterators may need cancellation/close depending on implementation.

## Test Signals
Tests should verify iterator covariance, `asList` behavior for empty/large sequences, and integration with `AsyncUtil.collect`.
